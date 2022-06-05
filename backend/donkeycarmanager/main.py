from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from donkeycarmanager import models
from donkeycarmanager.database import engine
from donkeycarmanager.dependencies import get_db, sm, get_sio
from donkeycarmanager.routers import players, driving_waiting_queue, cars, races, laptimers, workers

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
app.include_router(workers.router)


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
