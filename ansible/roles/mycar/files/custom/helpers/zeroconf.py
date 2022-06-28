import logging
import socket
from typing import Optional

from zeroconf import Zeroconf
from pydantic import BaseModel

ZERO_CONF_MAX_TRY = 15

class ZeroConfResult(BaseModel):
    ip: str
    port: int


def find_zero_conf_service(service_type: str, name: str, max_retry = ZERO_CONF_MAX_TRY) -> Optional[ZeroConfResult]:
    """
    Find zeroconf service IP addr, may try multiple times.

    Service should advertise at "_{name}.{type}"
    :param service_type: service category
    :param name: service name
    :param max_retry: Number of retries
    :return: result with address and port
    """
    zeroconf = Zeroconf()
    logger = logging.getLogger( __name__  + ".fin_zero_conf_service_host")

    nb_remaining_try = max_retry
    full_name = f"_{name}.{service_type}"

    while nb_remaining_try > 0:
        logger.debug('Trying to find service "%s" using zeroconf, remaining try : %i', full_name, nb_remaining_try)
        try:

            service = zeroconf.get_service_info(service_type, full_name)

            if service is not None:  # API found
                ip = socket.inet_ntoa(service.addresses[0])
                port = service.port
                logger.debug('Found service %s IP at : %s:%i', full_name, ip, port)
                return ZeroConfResult(ip=ip, port=port)
        except Exception as e:
            if nb_remaining_try - 1 <= 0:  # last try display error
                logger.error('Last attempt using zeroconf got the following error : %s')
                logger.exception(e)
        finally:
            zeroconf.close()

        nb_remaining_try -= 1

    return None