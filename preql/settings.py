import sys
import logging

logging.basicConfig(level=logging.INFO,
                    format="(%(levelname)s) %(name)s -- %(message)s",
                    )#datefmt='%m-%d %H:%M')

optimize = True
cache = False

debug = False # not sys.flags.optimize
print_sql = False


try:
    from .local_settings import *
except ImportError:
    pass


