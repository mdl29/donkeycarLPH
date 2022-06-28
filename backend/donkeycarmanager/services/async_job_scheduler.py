import asyncio
import logging
from typing import Dict, List

import socketio
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from donkeycarmanager.emitters.jobs_without_job_sched import on_job_update_without_sched, on_job_change_worker_notify
from donkeycarmanager.helpers.conditional_events import AsyncConditionalEvents, AsyncCondEventsOperator
from donkeycarmanager.helpers.registable_event import AsyncRegistableEvent
from donkeycarmanager.models import Job, Worker
from donkeycarmanager.schemas import WorkerState, WorkerType, JobState

import donkeycarmanager.crud.jobs_read as crudJobs
import donkeycarmanager.crud.workers_read as crudWorkers


class AsyncJobScheduler:

    def __init__(self, db: Session, sio: socketio.AsyncServer):
        super(AsyncJobScheduler, self).__init__()
        self._db = db
        self._sio = sio
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

        # Events for each type of jobs waiting for a specific worker_type
        self.job_waiting_events_by_type: Dict[str, AsyncRegistableEvent] = {}  # Keys are worker_type.name
        # Events for all available worker for each worker_type
        self.worker_available_events_by_type: Dict[str, AsyncRegistableEvent] = {}  # Keys are worker_type.name

        # Combo of job available and worker for each worker_type
        self.compatible_job_and_worker_events: Dict[str, AsyncConditionalEvents] = {}  # Keys are worker_type.name
        for worker_type in WorkerType:
            job_waiting_event = AsyncRegistableEvent()
            worker_available_event = AsyncRegistableEvent()
            self.job_waiting_events_by_type[worker_type] = job_waiting_event
            self.worker_available_events_by_type[worker_type] = worker_available_event

            self.compatible_job_and_worker_events[worker_type] =\
                AsyncConditionalEvents([job_waiting_event, worker_available_event], operator=AsyncCondEventsOperator.AND)

        # Any compatible job and worker, of all worker_type
        self.a_compatible_job_and_worker_any_event =\
            AsyncConditionalEvents(self.compatible_job_and_worker_events.values(), operator=AsyncCondEventsOperator.OR)

    async def on_job_changed(self, job: Job):
        """
        A maybe new waiting job is here \o/ will notify if needed.
        :param job: job
        """
        if job.state == JobState.WAITING and job.worker_id is None:
            self.logger.debug('job_waiting_events_by_type set for worker type: %s', job.worker_type)
            await self.job_waiting_events_by_type[job.worker_type].set()
            return

        if job.state == JobState.CANCELLING and job.worker_id is None:
            self.logger.debug('Ask to cancel a job that as no worker,' +
                              'passing from CANCELLING state to CANCELLED directly, job_id: %i', job.job_id)
            db_job_event = inspect(job).session  # We need to use the same DB instance as the one attached to this job
            db_job_event.refresh(job)
            job.state = JobState.CANCELLED
            db_job_event.commit()
            await on_job_update_without_sched(db_job_event, self._sio, job)
            return

    async def on_worker_changed(self, worker: Worker):
        """
        A new worker is in available state.
        :param worker: worker
        """
        if self.is_available_worker(worker):
            self.logger.debug('worker_available_events_by_type set for worker type: %s', worker.type)
            await self.worker_available_events_by_type[worker.type].set()

    async def refresh_waiting_jobs_by_types(self):
        """
        For all worker_types set event when a job is available.
        """
        for worker_type in WorkerType:
            jobs = self.waiting_jobs_by_worker_type(worker_type)

            if len(jobs) > 0:  # We have WAITING jobs for this worker type
                await self.job_waiting_events_by_type[worker_type].set()

    def waiting_jobs_by_worker_type(self, worker_type: WorkerType) -> List[Job]:
        """
        Find all waiting jobs for a worker type (by_rank)
        :param worker_type: type of worker
        :return: All available jobs.
        """
        return crudJobs.get_jobs(self._db, limit=1, by_rank=True,
                                 no_worker=True, worker_type=worker_type,
                                 job_states=[
                                     JobState.WAITING, JobState.RUNNING, JobState.PAUSING, JobState.PAUSED,
                                     JobState.CANCELLING])

    async def refresh_available_workers_by_types(self):
        """
        For all worker_types set event when worker is available.
        """
        for worker_type in WorkerType:
            workers = self.available_workers(worker_type)

            if len(workers) > 0:
                await self.worker_available_events_by_type[worker_type].set()

    def available_workers(self, worker_type: WorkerType) -> List[Worker]:
        """
        Find available workers for a worker type.
        :param worker_type: type of worker
        :return: List of available workers.
        """
        workers = crudWorkers.get_workers(self._db, worker_state=WorkerState.AVAILABLE, worker_type=worker_type)
        workers_without_waiting_jobs = []

        for worker in workers:
            if not self.is_available_worker(worker): # This worker already as job, shouldn't be considered as available
                continue
            else:
                workers_without_waiting_jobs.append(worker)

        return workers_without_waiting_jobs

    def is_available_worker(self, worker: Worker) -> bool:
        """
        Check if a worker is really available, meaning it as no waiting jobs already.
        :param worker: worker
        :return: True if it's available, False otherwise.
        """
        if worker.state != WorkerState.AVAILABLE:
            return False

        jobs = crudJobs.get_jobs(self._db, job_states=[JobState.WAITING], worker_id=worker.worker_id)
        return len(jobs) == 0 # This worker doesn't have any waiting jobs

    async def start(self):
        """ Start the async loop, should be done where we have access to an async loop"""
        asyncio.create_task(self.run())

    async def run(self):
        """
        Main scheduler engine.
        """
        while True:
            self.a_compatible_job_and_worker_any_event.clear()

            await self.refresh_waiting_jobs_by_types()  # Fetch waiting job that might pop during our last job scheduling
            await self.refresh_available_workers_by_types()  # Fetch available workers

            await self.a_compatible_job_and_worker_any_event.wait()

            # We need to find the matching jobs and workers by worker_type
            for worker_type in WorkerType:
                if await self.compatible_job_and_worker_events[worker_type].is_set():
                    jobs = self.waiting_jobs_by_worker_type(worker_type)
                    workers = self.available_workers(worker_type)

                    for worker in workers:
                        if len(jobs) > 0:
                            job = jobs.pop(0)
                            job.worker_id = worker.worker_id
                            self._db.commit()

                            self.logger.debug('Assigning worker_id: %i to job_id: %i, of type : %s',
                                              worker.worker_id, job.job_id, worker_type)
                            await on_job_change_worker_notify(self._db, self._sio, job_changed=job) # TODO find a way to call it inside the thread
                        else:
                            break  # No more jobs

                    # We did everything we can for this worker_type, cleaning all events flags associated
                    self.worker_available_events_by_type[worker_type].clear()
                    self.job_waiting_events_by_type[worker_type].clear()
                    self.compatible_job_and_worker_events[worker_type].clear()
