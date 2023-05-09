import json
import logging
import os
from datetime import datetime
from ftplib import FTP
from typing import Optional, Tuple, NoReturn, Any

from dkmanager_worker.helpers.RegistableEvents import RegistableEvent
from dkmanager_worker.helpers.conditional_events import ConditionalEvents, CondEventsOperator
from dkmanager_worker.models.schemas import JobCreate, WorkerType, JobState, Job, EventJobChanged, Stage

from custom.car.helpers.os import clean_directory_content, make_tarfile
from custom.car.services.jobs.job_drive import JobDrive, JobDriveStage

TMP_TAR_FILE_PATH = '/tmp/donkeycarLPH-data.tar.gz'
FTP_DATASET_FOLDER = 'datasets'

DEFAULT_AI_ASSISTED_JOB_DRIVE_TIME = 2 * 60 # Default drive time is 2min

class JobRecord(JobDrive):

    def __init__(self, **kwargs):
        super(JobRecord, self).__init__(**kwargs)

        # We don't need user confirmation for recording as the user doesn't change
        self.drive_stage = JobDriveStage.USER_CONFIRMED

        # We don't want drive confirmation message
        self.by_pass_drive_finished_confirmation = True

        self.is_recording = RegistableEvent()  # Will be set when the user is recording
        self.is_training_finished = RegistableEvent() # Will be set when the user training job is finished

        self.training_job: Optional[Job] = None # Will old the training job, available when is_training_finished is set.

        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)


    def clean_data_folder(self) -> NoReturn:
        """
        Clean recording folder.
        """
        self.logger.debug('Job[job_id: %i] cleaning %s',
                          self.get_id(), self.tub_path)
        clean_directory_content(self.tub_path)
        os.mkdir(f"{self.tub_path}/images")

    def start_recording(self) -> NoReturn:
        self.logger.debug('Job[job_id: %i] Starting recording for user %s',
                              self.get_id(), self.job_data.player.player_pseudo)
        self.clean_data_folder()
        # Would need to reset tub_writer
        self.tub_writer.reset()

        # To have the json manifest inited
        self.is_recording.set()

    def compress_transfert_data(self) -> str:
        """
        Compress and transfert data in FTP.

        :returns: Remote file path.
        """
        # Create tar file with all data, it speed up the transfer process as we have a lot of small files
        self.logger.debug('Job[job_id: %i] Creating tar file at %s, with all data in %s',
                          self.get_id(), TMP_TAR_FILE_PATH, self.tub_path)
        make_tarfile(TMP_TAR_FILE_PATH, self.tub_path)

        # Transfer file to FTP
        ftp = FTP()
        connect_res = ftp.connect(host=self.ftp.ip, port=self.ftp.port)
        login_res = ftp.login(user='donkeycarlph', passwd='donkeycarlph')
        d_now = datetime.utcnow()
        remote_archive_name = f'{d_now.strftime("%Y-%m-%d_%H:%I")}_{self.car.name}_p{self.job_data.player_id}_j{self.job_data.job_id}.tar.gz'

        if not (FTP_DATASET_FOLDER in ftp.nlst()):
            self.logger.debug('Job[job_id: %i] Creating FTP folder "%s"', self.get_id(), FTP_DATASET_FOLDER)
            ftp.mkd(FTP_DATASET_FOLDER)

        ftp.cwd(FTP_DATASET_FOLDER)
        file = open(TMP_TAR_FILE_PATH, 'rb')
        self.logger.debug('Job[job_id: %i] Transferring to "%s"', self.get_id(), remote_archive_name)
        res = ftp.storbinary(f'STOR {remote_archive_name}', file)
        self.logger.debug('Job[job_id: %i] Transfer result : %s', self.get_id(), res)
        file.close()

        ftp.close()

        # Clean tar
        os.remove(TMP_TAR_FILE_PATH)

        return f'{FTP_DATASET_FOLDER}/{remote_archive_name}'

    def run_threaded(self,
                     user_throttle=None,
                     laptimer_current_start_lap_datetime: Optional[datetime] = None,
                     laptimer_current_lap_duration: Optional[int] = None,
                     laptimer_last_lap_start_datetime: Optional[datetime] = None,
                     laptimer_last_lap_duration: Optional[int] = None,
                     laptimer_last_lap_end_date_time: Optional[datetime] = None,
                     laptimer_laps_total: Optional[int] = None,
                     controller_x_pressed: Optional[bool] = False,
                     cam_image_array: Optional[Any] = None
                     ) -> Tuple[float, str, bool, bool]:
        user_throttle, job_name, laptimer_reset_all, recording_state, pilote_angle, pilote_throttle, user_mode =  super(JobRecord, self).run_threaded(
                user_throttle,
                laptimer_current_start_lap_datetime,
                laptimer_current_lap_duration,
                laptimer_last_lap_start_datetime,
                laptimer_last_lap_duration,
                laptimer_last_lap_end_date_time,
                laptimer_laps_total,
                controller_x_pressed,
                cam_image_array)
        job_name = 'RECORD'
        user_mode = 'user'


        # Recording stays enabled until drive is finished
        recording_state = self.drive_stage == JobDriveStage.USER_DRIVING

        if recording_state and not self.is_recording.isSet():
            self.start_recording()

        return user_throttle,\
               job_name,\
               laptimer_reset_all,\
               recording_state,\
               pilote_angle,\
               pilote_throttle,\
               user_mode

    def on_training_job_update(self, event_dict: dict):
        """
        When the training job is updated.

        :param event: The update job event.
        """
        event = EventJobChanged.parse_obj(event_dict)
        self.logger.debug('on_training_job_update: with event : %r', event)

        self.training_job = event.job # Update training job datas

        if event.job.state == JobState.FAILED:
            self.logger.debug('Job[job_id: %i] Training job (id: %i) failed with fail_details : %s', self.get_id(),
                              event.job.job_id, event.job.fail_details)
            self.display_screen_msg(f'Échec de l\'entrainement (j{event.job.job_id}) ❌')
            self.screen_msg('')
        elif event.job.state == JobState.CANCELLED:
            self.logger.debug('Job[job_id: %i] Training job (id: %i) cancelled', self.get_id(), event.job.job_id)
            self.display_screen_msg(f'Entrainement annulé (j{event.job.job_id}) ❌')
            self.screen_msg('')
        elif event.job.state == JobState.CANCELLING:
            self.logger.debug('Job[job_id: %i] Training job (id: %i) cancelling', self.get_id(), event.job.job_id)
            self.display_screen_msg(f'Annulation de l\'entrainement (j{event.job.job_id}) ⏳...')
        elif event.job.state == JobState.RUNNING:
            self.logger.debug('Job[job_id: %i] Training job (id: %i) is running \\o/', self.get_id(), event.job.job_id)
            self.display_screen_msg("Entrainement du modèle en cours 🎓⏳️️... ")
        elif event.job.state == JobState.SUCCEED:
            self.logger.debug('Job[job_id: %i] Training job (id: %i) finished ... yeah baby', self.get_id(),
                              event.job.job_id)
            self.is_training_finished.set()
            self.sio.handlers['/'][f'one_job_id.{event.job.job_id}.updated']  # Remove socket IO handler

    def create_ai_assisted_job(self, model_archive_path: str) -> Job:
        """
        Create the drivin model job associated to current player car and a model (stored on the FTP).

        :param model_archive_path: Path to the archive.
        """
        parameters = json.loads(self.job_data.parameters)
        model_drive_time = parameters["model_drive_time"] if "model_drive_time" in parameters else DEFAULT_AI_ASSISTED_JOB_DRIVE_TIME
        drive_model_job = {
            'worker_type': WorkerType.CAR,
            'state': JobState.WAITING,
            'player_id': self.job_data.player_id,
            'worker_id': self.job_data.worker_id,  # Had to be run on the same car
            'name': Stage.AI_ASSISTED,
            'parameters': json.dumps({
                'model_remote_archive': model_archive_path,
                'drive_time': model_drive_time
            })
        }
        model_job_create_req = JobCreate(**drive_model_job)
        self.logger.debug('[job_id: %i] Creating model driving job, for player: %i (%s)', self.get_id(),
                          self.job_data.player.player_id, self.job_data.player.player_pseudo)
        drive_model_job: Job = self.api.create_job(model_job_create_req)
        drive_model_job = self.api.job_move_after(drive_model_job.job_id, after_job_id=self.job_data.job_id)
        self.logger.debug('[job_id: %i] Created model driving job id: %i, for player: %i (%s)', self.get_id(),
                          drive_model_job.job_id, self.job_data.player.player_id, self.job_data.player.player_pseudo)
        return drive_model_job

    def start_training(self, remote_dataset_path):
        """
        Start the trainning of the model.

        :param remote_dataset_path: remote dataset path
        """
        training_job_dict = {
            'worker_type': WorkerType.AI_TRAINER,
            'name': 'TRAIN',
            'parameters': json.dumps({
                'dataset_file_ftp_path': remote_dataset_path
            }),
            'state': JobState.WAITING,
            'player_id': self.job_data.player_id,
            'worker_id': None
        }
        training_job = JobCreate(**training_job_dict)
        self.logger.debug('[job_id: %i] Creating training job, for player: %i (%s)', self.get_id(),
                          self.job_data.player.player_id, self.job_data.player.player_pseudo)
        training_job: Job = self.api.create_job(training_job)
        self.logger.debug('[job_id: %i] Training job created with ID %i', self.get_id(),
                          training_job.job_id)
        self.logger.debug('[job_id: %i]  Telling the user it\'s model training is launched',
                          self.get_id())
        self.display_screen_msg("Entrainement du modèle on attend un prof 🎓️... ")

        event_name = f'one_job_id.{training_job.job_id}.updated'
        self.logger.debug("Job[job_id: %i] Listening to '%s' events", self.get_id(), event_name)
        self.sio.on(event_name, self.on_training_job_update)

    def run_job(self, resumed: bool = False) -> None:
        self.logger.debug('Job[job_id: %i] Starting RECORD job, will execute Drive job', self.get_id())
        super(JobRecord, self).run_job()

        if self.event_cancelled.isSet() or self.event_paused.isSet():
            return
        elif self.drive_stage == JobDriveStage.DRIVE_FINISHED:
            self.logger.debug('Job[job_id: %i] Finish drive with success',
                              self.get_id())
            self.screen_msg("UI-train")
            self.logger.debug('Job[job_id: %i] Sending data to server ......',
                              self.get_id())
            self.display_screen_msg("Fini ! Transfert de l'enregistrement ⏳...️")
            remote_dataset_path = self.compress_transfert_data()
            self.clean_data_folder()

            self.start_training(remote_dataset_path)

            with ConditionalEvents([self.event_cancelled, self.is_training_finished],
                                   operator=CondEventsOperator.OR) as training_finished_or_cancelled:
                training_finished_or_cancelled.wait()

            if self.event_cancelled.isSet():
                self.logger.debug('[job_id: %i] Cancelled during training waiting', self.get_id())
                self.screen_msg('')
                return
            elif self.is_training_finished.isSet():
                self.logger.debug('[job_id: %i] Training finished', self.get_id()) # Will already display a msg
                parameters = json.loads(self.training_job.parameters)
                model_archive_path = parameters['output:model_remote_archive']
                self.logger.debug('Job[job_id: %i] Training job (id: %i) model available here : %s', self.get_id(),
                                  self.training_job.job_id, model_archive_path)
                self.screen_msg('')
                self.create_ai_assisted_job(model_archive_path)

        else:
            self.logger.error('Job[job_id: %i] Something wrong hapened drive job didn\'t return with finish state',
                              self.get_id())
