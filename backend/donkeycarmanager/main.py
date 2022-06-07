from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect

from donkeycarmanager import models
from donkeycarmanager.crud.workers import get_worker
from donkeycarmanager.database import engine
from donkeycarmanager.dependencies import get_db, sm, get_sio
from donkeycarmanager.routers import players, driving_waiting_queue, cars, races, laptimers, workers, jobs
from donkeycarmanager.worker_heartbeat_manager import WorkerHeartbeatManager

models.Base.metadata.create_all(bind=engine)

open_api_tags_metadata = [
    {"name": "Players", "description": "Handle people willing to play with cars."},
    {"name": "DriveWaitingQueue", "description": "Manage pool of players.py waiting for their turn to drive a car."}
]

app = FastAPI(
    dependencies=[Depends(get_db), Depends(get_sio)],
    openapi_tags=open_api_tags_metadata)
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


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, ws_ping_interval=2, ws_ping_timeout=6, timeout_keep_alive=2)


if __name__ == "__main__":
    main()
