import os


def list_instances():
    prefix = '/srv/lava/instances'
    if not os.path.exists(prefix):
        return []
    return [os.path.join(prefix, x) for x in os.listdir(prefix)
            if os.path.isdir(os.path.join(prefix, x))]
