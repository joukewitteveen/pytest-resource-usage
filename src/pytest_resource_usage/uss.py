try:
    from .psutil_uss import *
except ImportError:
    # psutil may not be available; do not load the plugin
    pass
