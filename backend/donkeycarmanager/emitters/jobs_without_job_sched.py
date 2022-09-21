import json
import logging
from typing import NoReturn

import socketio
from sqlalchemy.orm import Session

from donkeycarmanager import models
from donkeycarmanager.crud.jobs_read import on_job_queue_order_changes
from donkeycarmanager.schemas import EventJobChanged

RANKING_STEP = 2000  # How much place by default between 2 players.py in driving waiting queue

logger = logging.getLogger(__name__)


# To avoid circular import we had to split notification events
# Circular import was : JobSched import emitters.jobs import JobSched

async def on_job_update_without_sched(db: Session, sio: socketio.AsyncServer,
                        job_changed: models.Job):
    # We always notify because changed could impact parameters, assigned worker ... so job list on cars need to be
    # updated to reflect those changes
    await on_job_update_notify_job_direct_watcher(db, sio, job_changed)
    await on_job_queue_order_changes(db, sio, jobs_changed=[job_changed])
    await on_job_change_worker_notify(db=db, sio=sio, job_changed=job_changed)


async def on_job_update_notify_job_direct_watcher(db: Session, sio: socketio.AsyncServer,
                        job_changed: models.Job) -> NoReturn:
    """
    Send event to people listening for this job updates specifically at one_job_id.JOB_ID.updated
    :param db: Database
    :param sio: Socket IO instance
    :param job_changed: Changed job
    """
    # Send socket IO event with all queue elements
    event = EventJobChanged(job=job_changed)
    event_json_payload = json.loads(event.json())  # Workaround to get pydantic deep conversion as dict
    event_name = f"one_job_id.{job_changed.job_id}.updated"
    logger.debug('on_job_update_notify_job_direct_watcher: emitting "%s" with : %s', event_name, event_json_payload)

    await sio.emit(event_name, event_json_payload)


async def on_job_change_worker_notify(db: Session, sio: socketio.AsyncServer,
                                      job_changed: models.Job) -> None:
    """
    Emit to notify a worker of "one" job change. Shouldn't be used to handle jobs orders.
    :param db: database
    :param sio: socketIO
    :param job_changed: Changed job.
    """
    if job_changed.worker_id is None:
        return

    # Send socket IO event with all queue elements
    event = EventJobChanged(job=job_changed)
    event_json_payload = json.loads(event.json())  # Workaround to get pydantic deep conversion as dict
    event_name = f"one_job.{job_changed.worker_id}.updated"
    logger.debug('on_one_job_change: emitting "%s" with : %s', event_name, event_json_payload)
    await sio.emit(event_name, event_json_payload)
