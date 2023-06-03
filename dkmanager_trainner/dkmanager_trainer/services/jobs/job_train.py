import json
import os.path
import tempfile
import logging
from datetime import datetime
from pathlib import Path
import shutil

import socketio
from ftplib import FTP
from typing import Dict, NoReturn

from dkmanager_worker.helpers.retry_action import retry
from dkmanager_worker.helpers.zeroconf import ServiceLocation
from dkmanager_worker.models.schemas import Job
from dkmanager_worker.services.manager_api_service import ManagerApiService

from dkmanager_trainer.helpers.os import uncompress_tarfile, make_tarfile
from dkmanager_worker.services.jobs.generic_job import GenericJob

import donkeycar as dk
from donkeycar.pipeline.training import train

TMP_DATAET_ARCHIVE_FILENAME = "dataset.tar.gz"
TMP_MODEL_ARCHIVE_FILENAME = "model.tar.gz"
TMP_DATASET_FOLDER_NAME = "dataset"
TMP_MODELS_FOLDER_NAME = "models"
FTP_MODELS_ARCHIVE_FOLDER_NAME = "models" # FTP folder were all models are stored
DATASET_INSIDE_ARCHIVE_DATA_FOLDER = "data" # Where catalog .json files are stored inside the dataset archive


CONFIG_PATH = "/home/paperspace/car/config.py" # TODO should be improved with parameters
MODEL_TYPE = "linear"

class JobTrain(GenericJob):

    def __init__(self,
                 parameters: Dict[str, any],
                 job_data: Job,
                 api: ManagerApiService, ftp: ServiceLocation,
                 sio: socketio.Client):
        """
        Init a train job.
        :param parameters: Job parameters (json parsed from API)
        :param job_data: Job entry.
        :param api: DonkeyCarManager API
        :param ftp: DonkeyCarManager FTP server location details
        :param sio: SocketIO to manager
        """
        super(JobTrain, self).__init__(parameters, job_data, api, ftp, sio)

        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)
        self.tmp_folder = None

    def lazy_temp_folder(self) -> str:
        """
        Return temp folder for this job or create one if not already done.
        :return:
        """
        if self.tmp_folder is None:
            self.tmp_folder = tempfile.TemporaryDirectory(prefix=f"job_train_{self.job_data.job_id}_")
            self.logger.debug('Job[job_id: %i] Tempory folder created at %s', self.get_id(), self.tmp_folder)

        return self.tmp_folder.name

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

    @retry(nb_max_retry=7, time_increment_between_attempts=5, fun_description='FTP download')
    def download_and_uncompress_dataset(self) -> str:
        """
        Download job data set to a tmp folder.
        :return: it's path
        """
        if not "dataset_file_ftp_path" in self.parameters:
            self.logger.error('No dataset_file_ftp_path key found in job parameters, can\'t do anything')
        file_location = self.parameters['dataset_file_ftp_path']
        file_ftp_folder = os.path.dirname(file_location)
        file_ftp_filename = os.path.basename(file_location)

        # Download file from FTP
        ftp = self.get_ftp()
        ftp.cwd(file_ftp_folder)

        # Test list files
        files = ftp.nlst()

        tmp_folder = self.lazy_temp_folder()
        destination_archive_path = f"{tmp_folder}/{TMP_DATAET_ARCHIVE_FILENAME}"
        with open(destination_archive_path, 'wb') as dest_file:
            self.logger.debug('Job[job_id: %i] Transfering %s to %s', self.get_id(), file_location, destination_archive_path)
            ftp.retrbinary(f'RETR {file_ftp_filename}', dest_file.write)

        ftp.close()

        # Uncompress archive
        tmp_dataset_destination = f"{tmp_folder}/{TMP_DATASET_FOLDER_NAME}"
        self.logger.debug('Job[job_id: %i] uncompression dataset archive from %s to %s',
                          self.get_id(), destination_archive_path, tmp_dataset_destination )
        uncompress_tarfile(destination_archive_path, tmp_dataset_destination)

        return f"{tmp_dataset_destination}/{DATASET_INSIDE_ARCHIVE_DATA_FOLDER}"

    @retry(nb_max_retry=7, time_increment_between_attempts=5, fun_description='FTP upload')
    def compress_and_upload_model(self, models_folder_path) -> str:
        """
        Upload model to server and return it's file name.
        :param models_folder_path: Folder containing mypilot.h5 file and might contains other model formats also.
        :return: FTP file path. All model path will start with models/xxxx.tar.gz
        """
        # Create tar file with all data, it speed up the transfer process as we have a lot of small files
        model_archive_path = f"{self.lazy_temp_folder()}/{TMP_MODEL_ARCHIVE_FILENAME}"
        self.logger.debug('Job[job_id: %i] Creating tar file at %s, with all data in %s',
                          self.get_id(), model_archive_path, models_folder_path)
        make_tarfile(output_filename=model_archive_path, source_dir=models_folder_path)

        # Transfer file to FTP
        ftp = FTP()
        ftp.connect(host=self.ftp.ip, port=self.ftp.port)
        ftp.login(user='donkeycarlph', passwd='donkeycarlph')
        d_now = datetime.utcnow()
        remote_archive_name = f'{d_now.strftime("%Y-%m-%d_%H:%I")}_p{self.job_data.player_id}_j{self.job_data.job_id}.tar.gz'

        if not (FTP_MODELS_ARCHIVE_FOLDER_NAME in ftp.nlst()):
            self.logger.debug('Job[job_id: %i] Creating FTP folder "%s"', self.get_id(), FTP_MODELS_ARCHIVE_FOLDER_NAME)
            ftp.mkd(FTP_MODELS_ARCHIVE_FOLDER_NAME)

        ftp.cwd(FTP_MODELS_ARCHIVE_FOLDER_NAME)
        with open(model_archive_path, 'rb') as file:
            self.logger.debug('Job[job_id: %i] Transferring to "%s"', self.get_id(), remote_archive_name)
            res = ftp.storbinary(f'STOR {remote_archive_name}', file)
            self.logger.debug('Job[job_id: %i] Transfer result : %s', self.get_id(), res)

        ftp.close()

        return f'{FTP_MODELS_ARCHIVE_FOLDER_NAME}/{remote_archive_name}'

    def clean(self) -> NoReturn:
        """
        Clean all temps files.
        """
        tmp_folder = self.lazy_temp_folder()
        self.logger.debug('Job[job_id: %i] Cleaning %s', self.get_id(), tmp_folder)
        shutil.rmtree(tmp_folder)

    @retry(nb_max_retry=2, time_increment_between_attempts=15, fun_description='Model training')
    def train_model(self, dataset_path) -> str:
        """
        Start a training of the model and return it's path (h5 folder path) when finished.
        :param dataset_path:
        :return:
        """
        self.logger.debug('Job[job_id: %i] Starting training with data from %s ....',
                          self.get_id(), dataset_path)
        models_folder = f"{self.lazy_temp_folder()}/{TMP_MODELS_FOLDER_NAME}"
        Path(models_folder).mkdir(parents=True, exist_ok=True)

        cfg = dk.load_config(config_path=CONFIG_PATH)
        tubs = dataset_path
        model = f"{models_folder}/mypilot.h5"
        model_type = MODEL_TYPE
        comment = None
        train(cfg, tubs, model, model_type, comment)

        return models_folder

    def run_job(self, resumed: bool = False) -> None:
        """
        Run the train job.
        :param resumed:
        :return:
        """

        dataset_path = self.download_and_uncompress_dataset()

        self.logger.debug('Job[job_id: %i] dataset_path: %s', self.get_id(), dataset_path)

        if self.event_cancelled.isSet():
            self.clean()
            return

        model_folder_path = self.train_model(dataset_path)

        if self.event_cancelled.isSet():
            self.clean()
            return

        ftp_models_archive = self.compress_and_upload_model(model_folder_path)
        self.clean()

        # Here goes the ugly part of outputting in the job's inputs 🙈💩
        job_parameters = json.loads(self.job_data.parameters)
        job_parameters['output:model_remote_archive'] = ftp_models_archive
        self.job_data.parameters = json.dumps(job_parameters)
        self.api.update_job(self.job_data)

        return
