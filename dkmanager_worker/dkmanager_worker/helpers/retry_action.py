import logging
import traceback
import time

logger = logging.getLogger(__name__)


def retry(nb_max_retry: int = 10, time_increment_between_attempts: int = 5,
          fun_description: str = "Func"):
    """
    Retry a lambda taking no arguments multiple times until it fail or nb_max_retry is reach or the callable succeed.
    Between each retry waiting time is increased.
    :nb_max_retry: Maximum number of attempts.
    :time_increment_between_attempts: Between each tentative will add this waiting time.
                                        time delta : tentative 0 - tentative 1 : time_increment_between_attempts in sec
                                        time delta : tentative 1 - tentative 2 : time_increment_between_attempts*2 in sec
                                        time delta : tentative 2 - tentative 3 : time_increment_between_attempts*3 in sec
    :fun_description: Used to describe the action / operation we are retrying in logs.
    :return: action return value
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            nb_tentative = 0
            wait_time = time_increment_between_attempts

            while nb_tentative < nb_max_retry:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning('%s tentative %i failled, waiting for %i secs before next retry',
                                        fun_description, nb_tentative, wait_time)
                    logger.warning(traceback.format_exc())

                time.sleep(wait_time)

                nb_tentative += 1
                wait_time += time_increment_between_attempts

            logger.error('%s, failed to execute after %i retry', fun_description, nb_tentative)

        return wrapper
    return decorator