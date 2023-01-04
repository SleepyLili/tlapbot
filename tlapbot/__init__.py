import os
import logging
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from tlapbot.db import get_db
from tlapbot.owncast_helpers import is_stream_live, give_points_to_chat


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Prepare config: set db to instance folder, then load default, then
    # overwrite it with config.py and redeems.py
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, "tlapbot.sqlite")
    )
    app.config.from_object('tlapbot.default_config')
    app.config.from_object('tlapbot.default_redeems')
    app.config.from_pyfile('config.py', silent=True)
    app.config.from_pyfile('redeems.py', silent=True)

    # Make logging work for gunicorn-ran instances of tlapbot.
    if app.config['GUNICORN']:
        gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
    
    # Check for wrong config that would break Tlapbot
    if len(app.config['PREFIX']) != 1:
        raise RuntimeError("Prefix is >1 character. "
                           "Change your config to set 1-character prefix.")

    # prepare webhooks and redeem dashboard blueprints
    from . import owncast_webhooks
    from . import owncast_redeem_dashboard
    app.register_blueprint(owncast_webhooks.bp)
    app.register_blueprint(owncast_redeem_dashboard.bp)

    # add db CLI commands
    from . import db
    db.init_app(app)
    app.cli.add_command(db.clear_queue_command)
    app.cli.add_command(db.refresh_counters_command)
    
    # scheduler job for giving points to users
    def proxy_job():
        with app.app_context():
            if is_stream_live():
                app.logger.info("Stream is LIVE. Giving points to chat.")
                give_points_to_chat(get_db())
            else:
                app.logger.info("Stream is NOT LIVE. (Not giving points to chat.)")

    # start scheduler that will give points to users
    points_giver = BackgroundScheduler()
    points_giver.add_job(proxy_job, 'interval', seconds=app.config['POINTS_CYCLE_TIME'])
    points_giver.start()

    return app


if __name__ == '__main__':
    create_app()
