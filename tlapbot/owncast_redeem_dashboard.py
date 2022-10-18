from flask import render_template, Blueprint, request
from tlapbot.db import get_db
from tlapbot.owncast_helpers import (pretty_redeem_queue, all_counters,
        read_users_points_from_username)
from datetime import datetime, timezone

bp = Blueprint('redeem_dashboard', __name__)


@bp.route('/dashboard', methods=['GET'])
def dashboard():
    db = get_db()
    queue = pretty_redeem_queue(db)
    counters = all_counters(db)
    username = request.args.get("username")
    if username is not None:
        user_points = read_users_points_from_username(db, username)
    else: 
        user_points = None
    utc_timezone = timezone.utc
    return render_template('dashboard.html',
                           queue=queue,
                           counters=counters,
                           username=username,
                           user_points=user_points,
                           utc_timezone=utc_timezone)
