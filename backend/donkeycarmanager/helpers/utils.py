
def dict_to_attr(obj: any, data: dict) -> None:
    """
    Map a dict on matching existing object attributes.
    :param obj: Object that will be updated
    :param data: Dict data.
    """
    for key, value in data.items():
        setattr(obj, key, value)
