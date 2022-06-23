import os
import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware


from donkeycarmanager.dependencies import get_db, sm, get_sio, get_job_scheduler, db
from donkeycarmanager.helpers.logging import setup_logging
from donkeycarmanager.routers import players, driving_waiting_queue, cars, races, laptimers, workers, jobs
from donkeycarmanager.services.async_job_scheduler import AsyncJobScheduler
from donkeycarmanager.services.zero_conf_service import ZeroConfService

from donkeycarmanager import models
from donkeycarmanager.database import engine

models.Base.metadata.create_all(bind=engine)

# Logging stuff, luanch after uvircorn
setup_logging()
if os.environ.get('DONKEYCARMANAGER_LOG_LEVEL') == "DEBUG": # Can't do better as it's started with uvicorn
    logging.getLogger('donkeycarmanager').setLevel(logging.DEBUG)

# Application exposition port
APP_PORT = 8000

# Name of the environment variable used to set the network interface that will be used to find server IP addr
NETWORK_INTERFACE_ENV_VAR_NAME = "NETWORK_INTERFACE"

open_api_tags_metadata = [
    {"name": "Players", "description": "Handle people willing to play with cars."},
    {"name": "DriveWaitingQueue", "description": "Manage pool of players.py waiting for their turn to drive a car."}
]

# ZeroConf, server discovery
interface_name = os.environ.get(NETWORK_INTERFACE_ENV_VAR_NAME)
server_zeroconf = ZeroConfService(app_port=APP_PORT, network_interface_name=interface_name)

app = FastAPI(
    dependencies=[Depends(get_db), Depends(get_sio), Depends(get_job_scheduler)],
    openapi_tags=open_api_tags_metadata,
    on_startup=[server_zeroconf.start, get_job_scheduler().start],
    on_shutdown=[server_zeroconf.stop])
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
sm.mount(app)  # Mount socketIO

# Routes
app.include_router(players.router)
app.include_router(driving_waiting_queue.router)
app.include_router(cars.router)
app.include_router(races.router)
app.include_router(laptimers.router)
app.include_router(jobs.router)
app.include_router(workers.router)
