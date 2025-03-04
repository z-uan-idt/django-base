def singleton(cls):
    instances = {}

    def decorator(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return decorator
