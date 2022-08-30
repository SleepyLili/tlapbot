import os
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from tlapbot.db import get_db
from tlapbot.owncast_helpers import give_points_to_chat

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('tlapbot.default_config')
    app.config.from_object('tlapbot.config')

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    from . import owncast_webhooks
    app.register_blueprint(owncast_webhooks.bp)
    db.init_app(app)

    def proxy_job():
        with app.app_context():
            give_points_to_chat(get_db())

    points_giver = BackgroundScheduler()
    points_giver.add_job(proxy_job, 'interval', seconds=10) # change to 10 minutes out of testing
    points_giver.start()

    return app



if __name__ == '__main__':
    create_app()