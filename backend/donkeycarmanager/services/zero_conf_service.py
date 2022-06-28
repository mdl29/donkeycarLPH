import socket
import logging
from typing import Optional

from typing_extensions import NoReturn
from zeroconf import IPVersion
from zeroconf.asyncio import AsyncZeroconf, AsyncServiceInfo

from donkeycarmanager.helpers.networking import get_interface_ip_addr


class ZeroConfService:

    def __init__(self, app_port: int,
                 app_ip: Optional[str] = None,
                 app_fqdn: Optional[str] = None,
                 network_interface_name: Optional[str] = None,
                 service_name: str = "donkeycarmanager",
                 service_type: str = "_http._tcp.local."):
        """
        :param app_port: current fastAPI port / uvicorn port
        :param app_ip: current fastAPI host / uvicorn host. Default will be using IP from network_interface_name.
        :param app_fqdn: The full qualified name of the server, default will use the current host 'hostname.local.'
        :param network_interface_name: The network interface name "wlan0", "eth0" where we can find the app_ip.
            Not required if you use app_ip.
        :param service_name:  Name of the service that will be advertise on the network,
            will be : "_"+service_name+"."+service_type
        :param service_type: Type if the service.
        """
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

        self.ip = app_ip if app_ip else get_interface_ip_addr(network_interface_name)
        fqdn = app_fqdn if app_fqdn else f"{socket.gethostname()}.local."

        self.logger.debug("Using ip %s", self.ip)
        self.logger.debug("Using FQDN %s", fqdn)

        self.service_info = AsyncServiceInfo(service_type,
            f"_{service_name}.{service_type}",
            addresses=[socket.inet_aton(self.ip)],
            port=app_port,
            server=fqdn)
        self.zeroconf: Optional[AsyncZeroconf]= None

    async def start(self):
        """
        Start registering the service on the network.
        """
        self.logger.info("Start broadcasting current server under %s with ip %s", self.service_info.name, self.ip)
        self.zeroconf = AsyncZeroconf(ip_version=IPVersion.V4Only)
        return await self.zeroconf.async_register_service(self.service_info)

    async def stop(self):
        """
        Stop registering the service on the network.
        """
        self.logger.info("Stop broadcasting current server under %s", self.service_info.name)
        await self.zeroconf.async_register_service(self.service_info)
        return await self.zeroconf.async_close()
