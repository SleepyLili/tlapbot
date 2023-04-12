import os
import sys
import multiprocessing
import tlapbot
from tlapbot import timezone
from waitress import serve

os.chdir(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.getcwd())
PYBIN = sys.executable

def startup(ip = '127.0.0.1', port = '5000', debug = False):
    timezone.setup()
    WSGI_Cfg = {
        "bind": ip + port,
        "workers": (multiprocessing.cpu_count() * 2) + 1,
        "debug": debug
    }
    APP = tlapbot.create_app()
    serve(APP, host = ip, port = port, WSGI_Cfg)
