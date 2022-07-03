import logging
import os
from datetime import datetime
from ftplib import FTP
from typing import Optional, Tuple, NoReturn

from custom.generic_worker.helpers.RegistableEvents import RegistableEvent
from custom.generic_worker.helpers.conditional_events import ConditionalEvents, CondEventsOperator
from custom.car.helpers.os import clean_directory_content, make_tarfile
from custom.car.services.jobs.job_drive import JobDrive, JobDriveStage

TMP_TAR_FILE_PATH = '/tmp/donkeycarLPH-data.tar.gz'
FTP_DATASET_FOLDER = 'datasets'

class JobRecord(JobDrive):

    def __init__(self, **kwargs):
        super(JobRecord, self).__init__(**kwargs)

        # We don't need user confirmation for recording as the user doesn't change
        self.drive_stage = JobDriveStage.USER_CONFIRMED

        # We don't want drive confirmation message
        self.by_pass_drive_finished_confirmation = True

        self.is_recording = RegistableEvent()  # Will be set when the user is recording

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

    def compress_transfert_data(self) -> NoReturn:
        """
        Compress and transfert data in FTP.
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

    def run_threaded(self,
                     user_throttle=None,
                     laptimer_current_start_lap_datetime: Optional[datetime] = None,
                     laptimer_current_lap_duration: Optional[int] = None,
                     laptimer_last_lap_start_datetime: Optional[datetime] = None,
                     laptimer_last_lap_duration: Optional[int] = None,
                     laptimer_last_lap_end_date_time: Optional[datetime] = None,
                     laptimer_laps_total: Optional[int] = None,
                     controller_x_pressed: Optional[bool] = False
                     ) -> Tuple[float, str, bool, bool]:
        user_throttle, job_name, laptimer_reset_all, recording_state =  super(JobRecord, self).run_threaded(
                user_throttle,
                laptimer_current_start_lap_datetime,
                laptimer_current_lap_duration,
                laptimer_last_lap_start_datetime,
                laptimer_last_lap_duration,
                laptimer_last_lap_end_date_time,
                laptimer_laps_total,
                controller_x_pressed)
        job_name = 'RECORD'


        # Recording stays enabled until drive is finished
        recording_state = self.drive_stage == JobDriveStage.USER_DRIVING

        if recording_state and not self.is_recording.isSet():
            self.start_recording()

        return user_throttle, job_name, laptimer_reset_all, recording_state


    def run_job(self, resumed: bool = False) -> None:
        self.logger.debug('Job[job_id: %i] Starting RECORD job, will execute Drive job', self.get_id())
        super(JobRecord, self).run_job()

        if self.event_cancelled.isSet() or self.event_paused.isSet():
            return
        elif self.drive_stage == JobDriveStage.DRIVE_FINISHED:
            self.logger.debug('Job[job_id: %i] Finish drive with success',
                              self.get_id())

            self.logger.debug('Job[job_id: %i] Sending data to server ......',
                              self.get_id())
            self.compress_transfert_data()
            self.clean_data_folder()

            self.logger.debug('[job_id: %i]  Telling the user it\'s finished and he need to press X to continue',
                              self.get_id())
            self.job_data.screen_msg = "Enregistrement fini ! [Cross] pour lancer le calcul du modèle"
            self.job_data.screen_msg_display = True
            self.api.update_job(self.job_data)

            with ConditionalEvents([self.event_cancelled, self.event_controller_x_pressed],
                                   operator=CondEventsOperator.OR) as x_pressed_or_cancelled:
                x_pressed_or_cancelled.wait()

            self.job_data.screen_msg = None
            self.job_data.screen_msg_display = False
            self.api.update_job(self.job_data)

        else:
            self.logger.error('Job[job_id: %i] Something wrong hapened drive job didn\'t return with finish state',
                              self.get_id())
