import os
import sys
import multiprocessing
from gunicorn.app.wsgiapp import WSGIApplication
import uvicorn
import tlapbot

os.chdir(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.getcwd())
PYBIN = sys.executable

class WSGIServer(WSGIApplication):
    def __init__(self, app_uri, options=None):
        self.options = options or {}
        self.app_uri = app_uri
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

def startup():
    WSGI_Cfg = {
        "workers": (multiprocessing.cpu_count() * 2) + 1,
        "worker_class": "uvicorn.workers.UvicornWorker"
    }

    WSGIServer("tlapbot:create_app", WSGI_Cfg).run()
