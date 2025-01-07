import sys
import os

def flush_print(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()
