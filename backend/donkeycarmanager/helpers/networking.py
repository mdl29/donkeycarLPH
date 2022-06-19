from netifaces import ifaddresses, AF_INET


def get_interface_ip_addr(interface_name: str) -> str:
    """
    Retreive an interface IP addr
    :param interface_name: Interface name. Eg: eth0, wlan0 ...
    :return: The ipv4 addr.
    """
    return ifaddresses(interface_name)[AF_INET][0]['addr']
