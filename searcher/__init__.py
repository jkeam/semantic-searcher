from os import makedirs, getenv

from flask import Flask
import searcher.models
from searcher.extensions import db

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    if test_config is None:
        app.config.from_prefixed_env()
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # database
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}@{getenv('DB_HOST')}:{getenv('DB_PORT', '5432')}/{getenv('DB_DATABASE')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # ensure the instance folder exists
    try:
        makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/healthz')
    def healthz():
        return 'Alive'

    from . import auth
    app.register_blueprint(auth.bp)

    from . import search
    app.register_blueprint(search.bp)
    app.add_url_rule('/', endpoint='index')

    return app
