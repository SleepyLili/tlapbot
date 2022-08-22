import os # for using paths in config

from flask import Flask

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
    from . import owncastWebhooks
    app.register_blueprint(owncastWebhooks.bp)
    db.init_app(app)

    return app



if __name__ == '__main__':
    create_app()