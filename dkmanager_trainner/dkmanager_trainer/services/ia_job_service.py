from datetime import datetime
from typing import NoReturn, Optional, Dict, Type, Tuple

import socketio
from dkmanager_worker.services.jobs.generic_job import GenericJob

from dkmanager_worker.services.manager_api_service import ManagerApiService
from dkmanager_worker.services.job_service import JobService
from dkmanager_worker.models.schemas import Worker, Job as JobModel, Car
# Match job name with job runnable instance
from dkmanager_worker.helpers.zeroconf import ServiceLocation

from dkmanager_trainer.services.jobs.job_train import JobTrain

JOB_NAME_TO_JOB_RUNNABLE: Dict[str, Type[GenericJob]] = {
    'TRAIN': JobTrain,
}


class IaJobService(JobService):

    def __init__(self, api: ManagerApiService, ftp: ServiceLocation,
                 sio: socketio.Client, worker: Worker):
        """
        :param api: API manager instance.
        :param sio: Socket IO client.
        :param worker: The current car worker.
        """
        super(IaJobService, self).__init__(api=api, ftp=ftp,
                                            sio=sio, worker=worker)

    def init_job_run(self, job: JobModel) -> GenericJob:
        """
        Return job instance form job definition.
        :param job: Job definition
        :return: A runnable / job thread to be started
        """
        job_run_class = JOB_NAME_TO_JOB_RUNNABLE.get(job.name)

        if job_run_class is None:
            #TODO display log error
            # Throw an error
            return None

        parameters = self.parse_job_parameters(job.parameters)

        job_run_instance = job_run_class(
            parameters=parameters, job_data=job,
            api=self._api, ftp=self._ftp, sio=self._sio)
        return job_run_instance

    def on_before_new_job_start(self) -> NoReturn:
        """
        Executed when a new job is selected for a run.
        At this stage current_running_job is already setted with the new job
        """
        super(IaJobService, self).on_before_new_job_start()

    def on_current_job_ends(self) -> NoReturn:
        """
        Executed when the current job execution as finished, final state is setted.
        Should be overridden. Worker is set AVAILABLE just after it.
        """
        super(IaJobService, self).on_current_job_ends()
