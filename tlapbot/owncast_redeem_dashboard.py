from flask import render_template, Blueprint
from tlapbot.db import get_db
from tlapbot.owncast_helpers import pretty_redeem_queue, all_counters
from datetime import datetime, timezone

bp = Blueprint('redeem_dashboard', __name__)


@bp.route('/dashboard', methods=['GET'])
def dashboard():
    db = get_db()
    queue = pretty_redeem_queue(db)
    counters = all_counters(db)
    utc_timezone = timezone.utc
    return render_template('dashboard.html',
                           queue=queue,
                           counters=counters,
                           utc_timezone=utc_timezone)
