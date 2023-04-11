import time
from datetime import datetime
import pytz
from tzlocal import get_localzone

def setup():
    # get local timezone
    local_tz = get_localzone()
    ts = time.time()
    utc_now, now = datetime.utcfromtimestamp(ts), datetime.fromtimestamp(ts)

    local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(local_tz) # utc -> local
    assert local_now.replace(tzinfo=None) == now
