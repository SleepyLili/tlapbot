import os
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
    app.config.from_pyfile('config.py')
    app.config.from_pyfile('redeems.py')

    # prepare webhooks and redeem dashboard blueprints
    from . import owncast_webhooks
    from . import owncast_redeem_dashboard
    app.register_blueprint(owncast_webhooks.bp)
    app.register_blueprint(owncast_redeem_dashboard.bp)

    # add db initialization CLI command
    from . import db
    db.init_app(app)

    # add clear queue CLI command
    from . import owncast_helpers
    app.cli.add_command(owncast_helpers.clear_queue_command)

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
