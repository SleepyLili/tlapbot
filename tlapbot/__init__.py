import os
import time
import logging
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from tlapbot.db import get_db
from tlapbot.owncast_helpers import is_stream_live, give_points_to_chat

logger = logging.getLogger('tlapbot')
logger.setLevel(logging.INFO)

def get_instance(app, path):
    """Return the path with the instance folder as it's parent."""

    return os.path.join(app.instance_path, path)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Log incoming requests (useful for debugging)
    @app.after_request
    def after_request(response):

        # Don't log unless explicitly enabled
        if not app.config['ENABLE_LOGGING']:
            return

        timestamp = time.strftime('[%Y-%b-%d %H:%M]')
        logger.info('%s %s %s %s %s %s - %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status, request.data or "NODATA")
        return response

    # Prepare config: set db to instance folder, then load default, then
    # overwrite it with config.py and redeems.py
    app.config.from_mapping(
        DATABASE=get_instance(app, "tlapbot.sqlite")
    )
    app.config.from_object('tlapbot.default_config')
    app.config.from_object('tlapbot.default_redeems')
    app.config.from_pyfile(get_instance(app, 'config.py'), silent=True)
    app.config.from_pyfile(get_instance(app, 'redeems.py'), silent=True)

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
                give_points_to_chat(get_db())

    # start scheduler that will give points to users
    points_giver = BackgroundScheduler()
    points_giver.add_job(proxy_job, 'interval', seconds=app.config['POINTS_CYCLE_TIME'])
    points_giver.start()

    return app


if __name__ == '__main__':
    create_app()
