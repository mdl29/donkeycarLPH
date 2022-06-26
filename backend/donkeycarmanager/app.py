import os
import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from donkeycarmanager.dependencies import get_db, sm, get_sio, get_job_scheduler, heartbeat_manager, \
    get_heartbeat_manager
from donkeycarmanager.helpers.logging import setup_logging
from donkeycarmanager.routers import players, driving_waiting_queue, cars, races, laptimers, workers, jobs
from donkeycarmanager.services.async_job_scheduler import AsyncJobScheduler
from donkeycarmanager.services.zero_conf_service import ZeroConfService

from donkeycarmanager import models
from donkeycarmanager.database import engine
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

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
ZERO_CONF_API_TYPE = "_http._tcp.local."
ZERO_CONF_FTP_TYPE = "_ftp._tcp.local."

interface_name = os.environ.get(NETWORK_INTERFACE_ENV_VAR_NAME)
server_zeroconf = ZeroConfService(app_port=APP_PORT, service_type=ZERO_CONF_API_TYPE, network_interface_name=interface_name)
ftp_zeroconf = ZeroConfService(app_port=21, service_type=ZERO_CONF_FTP_TYPE, network_interface_name=interface_name)

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    dependencies=[Depends(get_db), Depends(get_sio), Depends(get_job_scheduler)],
    openapi_tags=open_api_tags_metadata,
    on_startup=[server_zeroconf.start, ftp_zeroconf.start, get_job_scheduler().start, heartbeat_manager.server_init],
    on_shutdown=[server_zeroconf.stop, ftp_zeroconf.stop])
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static") # mount swagger doc files

sm.mount(app)  # Mount socketIO

# Swagger ui configuration
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=" Donkeycar manager - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


# Redoc configuration
@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title="Donkeycar manager - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )

# Routes
app.include_router(players.router)
app.include_router(driving_waiting_queue.router)
app.include_router(cars.router)
app.include_router(races.router)
app.include_router(laptimers.router)
app.include_router(jobs.router)
app.include_router(workers.router)
