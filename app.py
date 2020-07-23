from flask import Flask, request, render_template
from flask_jwt_extended import JWTManager

from blacklist import BLACKLIST
from controller.user_controller import user
from controller.store_controller import store
from controller.item_controller import item
from model.dbconnect import db

app = Flask(__name__)


app.register_blueprint(user,url_prefix='/api/v1/user')
app.register_blueprint(store,url_prefix='/api/v1/store')
app.register_blueprint(item,url_prefix='/api/v1/item')

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql+psycopg2://postgres:@localhost/online_store_flask"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JWT_BLACKLIST_ENABLED"] = True  # enable blacklist feature
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = [
    "access",
    "refresh",
]
@app.before_first_request
def create_tables():
    db.create_all()


# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
#     return response



@app.route("/")
def hello():
    return "hello"

jwt  =  JWTManager(app)

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return (
        decrypted_token["jti"] in BLACKLIST
    )  # Here we blacklist particular JWTs that have been created in the past.


db.init_app(app)

if __name__ == '__main__':
    app.run(port=6060, debug=True)