from typing import Optional, NoReturn

import requests
import socket
import os
from netifaces import ifaddresses, AF_INET
from zeroconf import Zeroconf

from .schemas import Car, Worker, CarUpdate, WorkerCreate, WorkerState, WorkerType, CarCreate
from .worker_heartbeat import WorkerHeartBeat

RES_WORKERS = "workers"
RES_CARS = "cars"
ZERO_CONF_TYPE = "_http._tcp.local."
ZERO_CONF_NAME = "donkeycarmanager"

class CarManager:
    def __init__(self, api_origin: Optional[str] = None, network_interface: str = "wlan0"):
        """
        :param api_origin:  Optionnal api path, if not given will use zeroconf to find it and use the first found IP.
            Eg:
        :param network_interface: Network interface used to determine the car's IP addr.
        """
        self._api_origin = api_origin if api_origin else self._find_api_with_zero_conf()
        self._network_interface = network_interface  # Used to find IP addr
        self.worker: Optional[Worker] = None  # Worker associated to this car
        self.car: Car = self._update_or_create_car()  # Car representation of the current car

        if self.worker is None:
            raise Exception("No worker created for this car")

        # Worker heart beat, keep it alive and set it's state to available until job is taken
        self._worker_heartbeat = WorkerHeartBeat(api_origin=self._api_origin, worker=self.worker)
        self._worker_heartbeat.start()

    def _find_api_with_zero_conf(self) -> str:
        """
        Find API URL using zero conf.
        :return: The API URL
        """
        zeroconf = Zeroconf()
        url = None
        try:
            service = zeroconf.get_service_info(ZERO_CONF_TYPE, f"_{ZERO_CONF_NAME}.{ZERO_CONF_TYPE}")
            url = f"http://{socket.inet_ntoa(service.addresses[0])}:{service.port}"
        finally:
            zeroconf.close()

        return url

    def _update_or_create_car(self) -> Car:
        """
        Create car matching the name or update it, as car always have a worker associated it will also create the worker.
        :return:
        """
        car_name = self.get_car_name()
        current_car_basic_details = { 'name': car_name,
                          'ip': ifaddresses(self._network_interface)[AF_INET][0]['addr'],
                          'color': os.environ.get('CONTROLLER_LED_COLOR')}

        cars_url = f"{self._api_origin}/{RES_CARS}/"
        workers_url = f"{self._api_origin}/{RES_WORKERS}/"
        car_rest_url = f"{cars_url}{self.get_car_name()}"

        resp = requests.get(car_rest_url)
        if resp.status_code == 200:  # Need to update the car with current details
            api_car_refreshed = Car.parse_obj({**resp.json(), **current_car_basic_details})  # Override API car props to update them
            self.worker = api_car_refreshed.worker

            car_update = CarUpdate.parse_obj(api_car_refreshed)
            return Car.parse_obj(requests.put(car_rest_url, json=car_update.dict()).json())
        else:  # No existing car, so no worker need to create one also
            body = WorkerCreate(type=WorkerType.CAR, state=WorkerState.STOPPED)
            worker_resp = requests.post(workers_url, json=body.dict())
            self.worker = Worker.parse_obj(worker_resp.json())

            car = CarCreate(**current_car_basic_details, worker_id=self.worker.worker_id)
            return Car.parse_obj(requests.post(cars_url, json=car.dict()).json())

    def update_worker_state(self, state: WorkerState) -> NoReturn:
        """
        Update current car state.
        :param state: Current state
        """
        self.worker.state = state
        requests.put(f"{self._api_origin}/{RES_WORKERS}/{self.worker.worker_id}",
                            json=self.worker.json())

    def get_car_name(self) -> str:
        """
        :return: Current car name.
        """
        return socket.gethostname()

    def update(self):
        return

    def run_threaded(self):
        return

    def run(self):
        return self.run_threaded()
