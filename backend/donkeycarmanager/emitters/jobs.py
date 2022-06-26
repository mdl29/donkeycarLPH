import logging
import json

import socketio
from sqlalchemy.orm import Session

from donkeycarmanager import models
from donkeycarmanager.crud.jobs_read import on_job_queue_order_changes
from donkeycarmanager.emitters.jobs_without_job_sched import on_job_update_without_sched
from donkeycarmanager.schemas import EventJobChanged
from donkeycarmanager.services.async_job_scheduler import AsyncJobScheduler

RANKING_STEP = 2000  # How much place by default between 2 players.py in driving waiting queue

logger = logging.getLogger(__name__)


async def on_job_update(db: Session, sio: socketio.AsyncServer, job_sched: AsyncJobScheduler,
                        job_changed: models.Job):
    # We always notify because changed could impact parameters, assigned worker ... so job list on cars need to be
    # updated to reflect those changes
    await on_job_update_without_sched(db, sio, job_changed)
    await job_sched.on_job_changed(job=job_changed)
