import argparse
import logging
import time

from dkmanager_worker.helpers.zeroconf import ServiceLocation

from dkmanager_trainer.helpers.logging import setup_logging
from dkmanager_trainer.helpers.proxy_socks import set_sock_proxy
from dkmanager_trainer.services.ai_trainer_worker_service import AiTrainerWorkerService
from dkmanager_trainer.services.ia_job_service import IaJobService


def main():
    setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger("dkmanager_trainer").setLevel(
            logging.DEBUG if args.debug else logging.INFO)
        logging.getLogger("dkmanager_worker").setLevel(
            logging.DEBUG if args.debug else logging.INFO)

    logger = logging.getLogger("dkmanager_trainer")
    logger.info('Starting IA Trainer')

    #set_sock_proxy(host="localhost", port=6666)
    ftp_location = ServiceLocation(ip="localhost", port=21)
    ia_worker_service = AiTrainerWorkerService(api_origin="http://localhost:8000", ftp_location=ftp_location)

    while True: # TODO change that ugly thing
        time.sleep(1000)




if __name__ == "__main__":
    main()
