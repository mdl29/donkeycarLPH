import logging
import time
from datetime import datetime
from enum import Enum
from ftplib import FTP
from typing import Tuple, Optional, Union, Any, NoReturn
import donkeycar as dk
import os
import tempfile
import shutil

from dkmanager_worker.helpers.conditional_events import ConditionalEvents, CondEventsOperator

from custom.car.helpers.os import uncompress_tarfile
from custom.car.services.jobs.job import Job
from custom.car.services.race_service import RaceService

DEFAULT_DRIVE_TIME_SEC = 5*60 # Default drive time is 4min
MODEL_TYPE = "linear" # Currently fixed in the dkmanager-trainer implementation should be improved if needed

TMP_MODEL_ARCHIVE_FILENAME="model.tar.gz"
MODEL_PATH_INSIDE_ARCHIVE="models/mypilot.h5"


class JobAiAssistedStage(int, Enum):
    # Stages orders USER_NOT_CONFIRMED > USER_CONFIRMED > MODEL_DRIVING

    # At this stage, user isn't confirming meaning the job was started but we should pause it so that
    # the admin confirm manually to "resume" the job and asses it's the right user
    MODEL_INITIALIZATION = 0

    # user start moving and drive session fully started
    MODEL_DRIVING = 2

    # Driving session is finished
    DRIVE_FINISHED = 4


class JobAiAssisted(Job):

    __kl_singleton = None # Keras is heavy and should be instanced only once

    def __init__(self, **kwargs):
        super(JobAiAssisted, self).__init__(**kwargs)
        self.drive_stage: JobAiAssistedStage = JobAiAssistedStage.MODEL_INITIALIZATION

        self.drive_time = self.parameters["drive_time"] if "drive_time" in self.parameters else DEFAULT_DRIVE_TIME_SEC

        self.race_service = RaceService(self.api, self.job_data.player, car=self.car, max_duration=self.drive_time)
        self._kl_part: Optional[Union['KerasPilot', 'FastAiPilot']] = None # Will old the Keras part when initialized

        self.tmp_folder = None # Folder where model will be uncompressed, will be created automatically

        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

    @staticmethod
    def get_kl(cfg) -> Union['KerasPilot', 'FastAiPilot']:
        """
        Init or return already initialized Keras part.

        :param cfg: Donkeycar configuration, used only at first initialization (sadly)
        """
        if JobAiAssisted.__kl_singleton is None:
            JobAiAssisted.__kl_singleton = dk.utils.get_model_by_type(MODEL_TYPE, cfg)

        return JobAiAssisted.__kl_singleton

    def load_model(self, kl, model_path):
        """
        Function copy/pasted from manage.py now using clean logger.
        """
        start = time.time()
        self.logger.debug('[job_id: %i] loading model : %r', self.get_id(), model_path)
        kl.load(model_path)
        self.logger.debug('[job_id: %i] finished loading in %s sec.', self.get_id(), (str(time.time() - start)) )

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
                     ) -> Tuple[float, str, bool]:
        """
        Part run_threaded call.
        :param user_throttle: The user throttle, 0 when not moving.
        :return: [
            user_throttle,
            job_name,
            laptimer_reset_all,
            recording
            ]
        """
        # TODO add I/O
        super(JobAiAssisted, self).run_threaded(user_throttle,
                                                laptimer_current_start_lap_datetime,
                                                laptimer_current_lap_duration,
                                                laptimer_last_lap_start_datetime,
                                                laptimer_last_lap_duration,
                                                laptimer_last_lap_end_date_time,
                                                laptimer_laps_total,
                                                controller_x_pressed,
                                                cam_image_array)

        # Default values
        user_throttle = 0.0
        job_name = "DRIVE_MODEL"
        laptimer_reset_all = False
        recording_state = False
        pilot_angle = 0
        pilote_throttle = 0
        user_mode = 'auto_pilote'

        if self.drive_stage == JobAiAssistedStage.MODEL_DRIVING:
            laptimer_reset_all = self.race_service.handle_laptimer_outputs(
                laptimer_current_start_lap_datetime,
                laptimer_current_lap_duration,
                laptimer_last_lap_start_datetime,
                laptimer_last_lap_duration,
                laptimer_last_lap_end_date_time,
                laptimer_laps_total
            )

            if self._kl_part is not None:
                pilot_angle, pilote_throttle = self._kl_part.run(cam_image_array)

        return user_throttle, \
               job_name, \
               laptimer_reset_all, \
               recording_state, \
               pilot_angle, \
               pilote_throttle, \
               user_mode

    def get_ftp(self) -> FTP:
        """
        Return a connected FTP instance.
        :return:
        """
        # Transfer file to FTP
        ftp = FTP()
        connect_res = ftp.connect(host=self.ftp.ip, port=self.ftp.port)
        login_res = ftp.login(user='donkeycarlph', passwd='donkeycarlph')
        return ftp

    def lazy_temp_folder(self) -> str:
        """
        Return temp folder for this job or create one if not already done.
        :return:
        """
        if self.tmp_folder is None:
            self.tmp_folder = tempfile.TemporaryDirectory(prefix=f"job_ai_assisted_{self.job_data.job_id}_")
            self.logger.debug('Job[job_id: %i] Tempory folder created at %s', self.get_id(), self.tmp_folder)

        return self.tmp_folder.name

    def clean(self) -> NoReturn:
        """
        Clean all temps files.
        """
        tmp_folder = self.lazy_temp_folder()
        self.logger.debug('Job[job_id: %i] Cleaning %s', self.get_id(), tmp_folder)
        shutil.rmtree(tmp_folder, ignore_errors=True)

    def download_and_uncompress_model(self) -> str:
        """
        Download job model to a tmp folder.
        :return: it's path
        """
        if not "model_remote_archive" in self.parameters:
            self.logger.error('No model_remote_archive key found in job parameters, can\'t do anything')
        file_location = self.parameters['model_remote_archive']
        file_ftp_folder = os.path.dirname(file_location)
        file_ftp_filename = os.path.basename(file_location)

        # Download file from FTP
        ftp = self.get_ftp()
        ftp.cwd(file_ftp_folder)

        tmp_folder = self.lazy_temp_folder()
        destination_archive_path = f"{tmp_folder}/{TMP_MODEL_ARCHIVE_FILENAME}"
        with open(destination_archive_path, 'wb') as dest_file:
            self.logger.debug('Job[job_id: %i] Transfering %s to %s', self.get_id(), file_location,
                              destination_archive_path)
            ftp.retrbinary(f'RETR {file_ftp_filename}', dest_file.write)

        ftp.close()

        # Uncompress archive
        tmp_dataset_destination = tmp_folder
        self.logger.debug('Job[job_id: %i] uncompression dataset archive from %s to %s',
                          self.get_id(), destination_archive_path, tmp_dataset_destination)
        uncompress_tarfile(destination_archive_path, tmp_dataset_destination)

        return f"{tmp_dataset_destination}/{MODEL_PATH_INSIDE_ARCHIVE}"

    def init_keras_part(self, model_path: str):
        """
        Initialized the Keras part.

        :param model_path: Path to the model h5 file.
        """
        kl = JobAiAssisted.get_kl(self.cfg)

        if '.h5' in model_path or '.trt' in model_path or '.tflite' in \
                model_path or '.savedmodel' in model_path or '.pth':
            # load the whole model with weigths, etc
            self.load_model(kl, model_path)
        else:
            self.logger.error('Job[job_id: %i] ')
            raise Exception('Unknown model format')

        self._kl_part = kl

    def run_job(self, resumed: bool = False) -> None:
        self.logger.debug('Job[job_id: %i] Starting DRIVE_MODEL job', self.get_id())

        self.display_screen_msg("Entrainement fini 🎉 , récupération du modèle ⏳...")
        self.logger.debug('Job[job_id: %i] Will download model', self.get_id())
        model_path = self.download_and_uncompress_model()

        self.logger.debug('Job[job_id: %i] Model downloaded, initializing keras part', self.get_id())
        self.init_keras_part(model_path)
        self.logger.debug('Job[job_id: %i] Keras part initalized can now start drive the model, waiting for user confirmation', self.get_id())
        self.display_screen_msg("[Cross] Pour lancer le modèle")

        self.event_controller_x_pressed.clear()
        with ConditionalEvents([self.event_cancelled, self.event_controller_x_pressed],
                               operator=CondEventsOperator.OR) as x_pressed_cancelled:
            x_pressed_cancelled.wait()

        self.hidde_screen_msg()
        if self.event_cancelled.isSet():
            self.clean()
            return

        self.logger.debug(
            'Job[job_id: %i] X pressed, starting driving with model for %s seconds',
            self.get_id(), self.drive_time)
        self.drive_stage = JobAiAssistedStage.MODEL_DRIVING

        self.event_cancelled.wait(timeout=self.drive_time)

        if self.event_cancelled.isSet():
            self.clean()
            return

        self.clean()
