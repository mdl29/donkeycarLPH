import typing
import logging
import json
from typing import Optional, Union, Dict, List

import pydantic

from .schemas import Car, Worker, WorkerCreate, WorkerUpdate, CarCreate, CarUpdate, JobState, Job, \
    MassiveUpdateDeleteResult, Race, RaceCreate, LapTimerCreate, LapTimer, LapTimerUpdate, JobCreate
import requests
from datetime import date, datetime

RES_WORKERS = "workers"
RES_CARS = "cars"
RES_JOBS = "jobs"
RES_RACES = "races"
RES_LAPTIMERS = "laptimers"

T = pydantic.BaseModel


class CarManagerApiError(Exception):
    pass

class CarManagerApiService:

    def __init__(self, api_origin: str):
        """
        :param api_origin:  Optionnal api path, if not given will use zeroconf to find it and use the first found IP.
        """
        self._api_origin = api_origin
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

    @staticmethod
    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, (datetime, date)):
            return obj.astimezone().isoformat()  # Converts datetime to iso format with timezone
        raise TypeError("Type %s not serializable" % type(obj))

    @staticmethod
    def _json_dumps(dict: Dict) -> str:
        """ Convert to json handeling dates """
        return json.dumps(dict, default=CarManagerApiService.json_serial)

    def _create_resource(self, res: Union[CarCreate, WorkerCreate, JobCreate],
                         res_path: str, result_type: typing.Type[T], resource_name: str) -> T:
        """
        Create an api resource or raise an exception.
        :param res: input resource
        :param res_path: resource API path
        :param result_type: Pydantic type used to map the result
        :param resource_name: Understandable name that will be used in errors.
        :return: The created resource.
        """
        resp = requests.post(f"{self._api_origin}/{res_path}/",
                             data=self._json_dumps(res.dict()),
                             headers={'Content-Type': 'application/json'})
        if resp.status_code == 200:
            return result_type.parse_obj(resp.json())

        raise CarManagerApiError(f"Unable to create {resource_name} with : {res.dict()},"
                                 f" got status : {resp.status_code} with message : {resp.text}")

    def _get_resource(self, res_id: str,
                      res_path: str, result_type: typing.Type[T], resource_name: str) -> Optional[T]:
        """
        Get an api resource or raise an exception.
        :param res_id: input resource identifier
        :param res_path: resource API path
        :param result_type: Pydantic type used to map the result
        :param resource_name: Understandable name that will be used in errors.
        :return: The resource, None if 404 or raise if exception occured.
        """
        resp = requests.get(f"{self._api_origin}/{res_path}/{res_id}")
        if resp.status_code == 200:
            return result_type.parse_obj(resp.json())
        elif resp.status_code == 404:
            return None
        else:
            raise CarManagerApiError(f"Unable to fetch {resource_name} with ID : {res_id},"
                                     f" got status : {resp.status_code} with message : {resp.text}")

    def _get_resources(self, res_path: str, result_type: typing.Type[T], resource_name: str,
                       filters: Dict[str, any] = {}) -> Optional[T]:
        """
        Get an api list of resources or raise an exception.
        :param res_path: resource API path
        :param result_type: Pydantic type used to map the result
        :param resource_name: Understandable name that will be used in errors.
        :param filters: list of query parameters / filters
        :return: The resource, None if 404 or raise if exception occured.
        """
        resp = requests.get(f"{self._api_origin}/{res_path}/", params=filters)
        if resp.status_code == 200:
            resp_items = resp.json()
            res_items = list(map(lambda i: result_type.parse_obj(i), resp_items))
            return res_items
        elif resp.status_code == 404:
            return None
        else:
            raise CarManagerApiError(f"Unable to al fetch {resource_name},"
                                     f" got status : {resp.status_code} with message : {resp.text}")

    def _update_resource(self, res_id: str, res: Union[WorkerUpdate, CarUpdate],
                          res_path: str, result_type: typing.Type[T], resource_name: str) -> T:
        """
        Update an existing ressource.
        :param res_id: input resource ID
        :param res: input resource
        :param res_path: resource API path
        :param result_type: Pydantic type used to map the result
        :param resource_name: Understandable name that will be used in errors.
        :return: The updated resource.
        """
        resp = requests.put(f"{self._api_origin}/{res_path}/{res_id}",
                            data=self._json_dumps(res.dict()),
                            headers={'Content-Type': 'application/json'})
        if resp.status_code == 200:
            return result_type.parse_obj(resp.json())
        else:
            raise CarManagerApiError(f"Unable to update {resource_name} with ID : {res_id},"
                                     f" got status : {resp.status_code} with message : {resp.text}")

    def get_car(self, car_name: str) -> Optional[Car]:
        """
        Fetch a car using it's name
        :param car_name: Car name
        :return: Car if found.
        """
        return self._get_resource(car_name, RES_CARS, Car, "car")

    def create_car(self, car: CarCreate) -> Car:
        """
        Create a car.
        :param car: Car details
        :return: The create car
        """
        return self._create_resource(car, RES_CARS, Car, "car")

    def update_car(self, car: CarUpdate) -> Car:
        """
        Update a car.
        :param car: updated car.
        :return: The update car.
        """
        return self._update_resource(car.name, car, RES_CARS, Car, "car")

    def create_worker(self, worker: WorkerCreate) -> Worker:
        """
        Create a worker
        :param worker: Worker details
        :return: The created worker
        """
        return self._create_resource(worker, RES_WORKERS, Worker, "worker")

    def update_worker(self, worker: WorkerUpdate) -> Worker:
        """
        Update a worker.
        :param worker: updated worker.
        :return: The update worker.
        """
        return self._update_resource(worker.worker_id, worker, RES_WORKERS, Worker, "worker")

    def get_jobs(self, worker: Worker, job_states: Optional[List[JobState]]):
        """
        Fetch worker jobs with filer
        :param worker:
        :param job_states: All job stated wanted (OR operation is used)
        :return: The job list.
        """
        filters = {
            'worker_id': worker.worker_id
        }

        if job_states is not None:
            filters['job_states'] = job_states

        return self._get_resources(RES_JOBS, Job, "job", filters)

    def create_job(self, job: JobCreate) -> Job:
        """
        Create a job
        :param job:
        :return: Created job
        """
        return self._create_resource(job, RES_JOBS, Job, 'job')

    def update_job(self, job: Job) -> Job:
        """
        Update a job.
        :param job: Job to update
        :return: The updated job.
        """
        return self._update_resource(job.job_id, job, RES_JOBS, Job, "job")

    def job_move_after(self, job_id: int, after_job_id: int) -> Job:
        """
        Move job with job_id after the job having after_job_id
        :param job_id: Job to be moved
        :param after_job_id: Job reference.
        :return: The moved job.
        """
        resp = requests.post(f"{self._api_origin}/{RES_JOBS}/{job_id}/move_after",
                             data=self._json_dumps({ 'after_job_id': after_job_id }),
                             headers={'Content-Type': 'application/json'})
        if resp.status_code == 200:
            return Job.parse_obj(resp.json())

        raise CarManagerApiError(f"Unable to move job_id:{job_id} after after_job_id:{after_job_id} ")

    def job_move_before(self, job_id: int, before_job_id: int) -> Job:
        """
        Move job with job_id before the job having before_job_id
        :param job_id: Job to be moved
        :param before_job_id: Job reference.
        :return: The moved job.
        """
        resp = requests.post(f"{self._api_origin}/{RES_JOBS}/{job_id}/move_before",
                             data=self._json_dumps({'before_job_id': before_job_id}),
                             headers={'Content-Type': 'application/json'})
        if resp.status_code == 200:
            return Job.parse_obj(resp.json())

        raise CarManagerApiError(f"Unable to move job_id:{job_id} before before_job_id:{before_job_id} ")

    def worker_clean(self, worker: Worker, fail_details: str) -> int:
        """
        Clean all job of a worker (Running, Pausing, Paused, Cancelling...)
        Will set their state to fail with a fail_details.
        Use case : the worker start after reboot or fail, it clean it's jobs.
        :param worker: Worker whose jobs are going to be cleaned.
        :param fail_details: Reason why we are cleaning it.
        :return: Number of cleaned / modified job
        """
        self.logger.debug('Cleaning jobs for worker : %i', worker.worker_id)
        resp = requests.post(f"{self._api_origin}/{RES_WORKERS}/{worker.worker_id}/clean",
                            data=self._json_dumps({ 'fail_details': fail_details }),
                            headers={'Content-Type': 'application/json'})
        if resp.status_code == 200:
            return MassiveUpdateDeleteResult.parse_obj(resp.json()).nb_affected_items
        else:
            raise CarManagerApiError(f"Unable to clean worker with ID : {worker.worker_id},"
                                     f" got status : {resp.status_code} with message : {resp.text}")

    def create_race(self, race: RaceCreate) -> Race:
        """
        Create a race.
        :param race:
        :return: Created race.
        """
        return self._create_resource(race, RES_RACES, Race, "race")

    def create_laptimer(self, laptimer: LapTimerCreate) -> LapTimer:
        """
        Create a lap timer.
        :param laptimer:
        :return: Created laptimer.
        """
        return self._create_resource(laptimer, RES_LAPTIMERS, LapTimer, "laptimer")

    def update_laptimer(self, laptimer: LapTimerUpdate) -> LapTimer:
        """
        Create a lap timer.
        :param laptimer:
        :return: Created laptimer.
        """
        return self._update_resource(laptimer, RES_LAPTIMERS, LapTimer, "laptimer")
