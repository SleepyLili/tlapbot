
import os
import sys
import platform
import tlapbot
from tlapbot import timezone

os.chdir(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.getcwd())
PYBIN = sys.executable

if __name__ == '__main__':
    timezone.setup()
    FLASK_APP = "tlapbot"
    APP = tlapbot.create_app()
    if 'production' in sys.argv:
        if platform.uname().system.lower() == 'linux':
            from tlapbot import wsgi
            wsgi.startup()
            sys.exit()

    APP.run()
    sys.exit()
