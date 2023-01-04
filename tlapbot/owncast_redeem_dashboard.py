from flask import render_template, Blueprint, request, current_app
from tlapbot.db import get_db
from tlapbot.owncast_helpers import (pretty_redeem_queue, all_counters,
        read_all_users_with_username)
from datetime import datetime, timezone

bp = Blueprint('redeem_dashboard', __name__)


@bp.route('/dashboard', methods=['GET'])
def dashboard():
    db = get_db()
    username = request.args.get("username")
    if username is not None:
        users = read_all_users_with_username(db, username)
    else:
        users = []
    utc_timezone = timezone.utc
    return render_template('dashboard.html',
                           queue=pretty_redeem_queue(db),
                           counters=all_counters(db),
                           redeems=current_app.config['REDEEMS'],
                           prefix=current_app.config['PREFIX'],
                           username=username,
                           users=users,
                           utc_timezone=utc_timezone)
