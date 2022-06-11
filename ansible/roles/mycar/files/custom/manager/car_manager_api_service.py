import typing
import json
from typing import Optional, Union, Dict

import pydantic

from .schemas import Car, Worker, WorkerCreate, WorkerUpdate, CarCreate, CarUpdate, JobState, Job
import requests
from datetime import date, datetime

RES_WORKERS = "workers"
RES_CARS = "cars"
RES_JOBS = "jobs"

T = pydantic.BaseModel


class CarManagerApiError(Exception):
    pass

class CarManagerApiService:

    def __init__(self, api_origin: str):
        """
        :param api_origin:  Optionnal api path, if not given will use zeroconf to find it and use the first found IP.
        """
        self._api_origin = api_origin

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

    def _create_resource(self, res: Union[CarCreate, WorkerCreate],
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
        self._create_resource(car, RES_CARS, Car, "car")

    def update_car(self, car: CarUpdate) -> Car:
        """
        Update a car.
        :param car: updated car.
        :return: The update car.
        """
        self._update_resource(car.name, car, RES_CARS, Car, "car")

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
        self._update_resource(worker.worker_id, worker, RES_WORKERS, Worker, "worker")

    def get_jobs(self, worker: Worker, job_state: Optional[JobState]):
        """
        Fetch worker jobs with filer
        :param worker:
        :param job_state:
        :return: The job list.
        """
        filters = {
            'worker_id': worker.worker_id
        }

        if job_state is not None:
            filters['job_state'] = job_state.value

        return self._get_resources(RES_JOBS, Job, "job", filters)

    def update_job(self, job: Job) -> Job:
        """
        Update a job.
        :param job: Job to update
        :return: The updated job.
        """
        return self._update_resource(job.job_id, job, RES_JOBS, Job, "job")
