
import os
import sys
import platform
import tlapbot
from tlapbot import timezone

os.chdir(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.getcwd())
PYBIN = sys.executable

if getattr(sys, 'frozen', False):
    EXECUTABLE = sys.executable
else:
    EXECUTABLE = __file__

HELPER = [
    {
        "name":"pro",
        "usage":EXECUTABLE + " pro",
        "description":"Run tlapbot in a production mode."
    },
    {
        "name":"dev",
        "usage":EXECUTABLE + " dev",
        "description":"Run tlapbot in a development mode."
    },
    {
        "name":"ip",
        "usage":EXECUTABLE + " ip <IP>",
        "description":"Bind to the specific IP."
    },
    {
        "name":"port",
        "usage":EXECUTABLE + " port <Port>",
        "description":"Run on a specific port."
    },
    {
        "name":"debug",
        "usage":EXECUTABLE + " debug",
        "description":"Run in a debug mode."
    },
    {
        "name":"instance",
        "usage":EXECUTABLE + " instance <Path>",
        "description":"Setup configuration scripts in the specific path."
    },
    {
        "name":"help",
        "usage":EXECUTABLE + " help",
        "description":"Showing all available commands."
    }
]

def show_help(show_command=None):
    if show_command:
        for i in HELPER:
            if i['name'] == show_command:
                output_string = 'Tlapbot:Help > ' + show_command
                output_string += '\nUsage: ' + i['usage']
                output_string += '\nDescription:\n\t' + i['description']
                print(output_string)
                sys.exit()

        print('Tlapbot:Err > Unknown command \'' + show_command + '\'!')
        print('Tlapbot:Hint > Use \'help\' for listing all commands.')
        sys.exit()

    output_string = "Showing full help:\n"
    for i in HELPER:
        output_string += '\nTlapbot:Help > ' + i['name']
        output_string += '\nUsage: ' + i['usage']
        output_string += '\nDescription:\n\t' + i['description'] + '\n'

    print(output_string)
    print('Example overall usage: ' + EXECUTABLE + ' pro ip 127.0.0.1 port 5000')
    sys.exit()

if __name__ == '__main__':
    timezone.setup()
    FLASK_APP = "tlapbot"
    DEBUG=False

    if getattr(sys, 'frozen', False):
        INSTANCE = os.path.dirname(sys.executable) + '/instance'
    else:
        INSTANCE = os.path.dirname(__file__) + '/instance'

    if 'instance' in sys.argv:
        _ins_pos = sys.argv.index('instance')
        if len(sys.argv) <= _ins_pos + 1:
            print('Tlapbot:Err > missing path value.')
            sys.exit()
        INSTANCE = os.path.abspath(sys.argv[_ins_pos + 1])

    PORT = '5000'
    if 'port' in sys.argv:
        _port_pos = sys.argv.index('port')
        if len(sys.argv) <= _port_pos + 1:
            print('Tlapbot:Err > missing port value.')
            sys.exit()
        PORT = sys.argv[_port_pos + 1]

    IP = '127.0.0.1'
    if 'ip' in sys.argv:
        _ip_pos = sys.argv.index('ip')
        if len(sys.argv) <= _ip_pos + 1:
            print('Tlapbot:Err > missing IP value.')
            sys.exit()
        IP = sys.argv[_ip_pos + 1]

    if 'debug' in sys.argv:
        DEBUG=True

    if 'pro' in sys.argv:
        if platform.uname().system.lower() == 'linux':
            from tlapbot import wsgi
            wsgi.startup(IP, PORT, DEBUG, INSTANCE)
            sys.exit()
        elif platform.uname().system.lower() == 'windows':
            from tlapbot import wsgi_windows
            wsgi_windows.startup(IP, PORT, DEBUG, INSTANCE)
            sys.exit()
    elif 'dev' in sys.argv:
        APP = tlapbot.create_app(INSTANCE)
        APP.run(host = IP, port = PORT, debug = DEBUG)
        sys.exit()

    if 'help' in sys.argv:
        show_help()

    if len(sys.argv) > 1:
        show_help(sys.argv[1])
        sys.exit()

    show_help()
