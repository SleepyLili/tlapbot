from flask import render_template, Blueprint
from tlapbot.db import get_db
from tlapbot.owncast_helpers import pretty_redeem_queue

bp = Blueprint('redeem_dashboard', __name__)

@bp.route('/dashboard',methods=['GET'])
def dashboard():
    queue = pretty_redeem_queue(get_db())
    number_of_drinks = 0
    for row in queue:
        if row[1] == "drink":
            number_of_drinks += 1
    return render_template('dashboard.html', queue=queue, number_of_drinks=number_of_drinks)