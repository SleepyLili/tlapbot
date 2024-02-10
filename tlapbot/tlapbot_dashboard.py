from flask import render_template, Blueprint, request, current_app
from tlapbot.db import get_db
from tlapbot.redeems import all_active_counters, all_active_milestones, all_active_redeems, pretty_redeem_queue
from tlapbot.owncast_helpers import read_all_users_with_username
from datetime import timezone

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
                           counters=all_active_counters(db),
                           milestones=all_active_milestones(db),
                           redeems=all_active_redeems(),
                           prefix=current_app.config['PREFIX'],
                           passive=current_app.config['PASSIVE'],
                           username=username,
                           users=users,
                           utc_timezone=utc_timezone)
