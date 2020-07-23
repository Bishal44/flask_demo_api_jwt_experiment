from flask import Blueprint, request, jsonify
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
)

from blacklist import BLACKLIST
from model.user import UserModel
user = Blueprint("user", __name__)


BLANK_ERROR="'{}' cannot be left blank!"
USER_NOT_FOUND="User not found"
USER_ALREADY_EXIT="An user with name  already exists."
ERROR_INSERTING="An error occurred while inserting the item."
USER_OP="User '{}' sucessfully"
USER_LOG_OUT="User '<id={}>' successfully logged out."

_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    "username", type=str, required=True, help=BLANK_ERROR.format("username")
)
_user_parser.add_argument(
    "password", type=str, required=True, help=BLANK_ERROR.format("password")
)


@user.route('/show',methods=['GET'])
def show():
     user_id = request.values['userId']

     user = UserModel.find_by_id(user_id)
     if not user:
        return {"message": USER_NOT_FOUND}, 404
     return user.json(), 200


@user.route('/register',methods=['POST'])
def register():
    user_name = request.values['userName']
    password = request.values['password']
    if UserModel.find_by_username(user_name):
        return {"message": USER_ALREADY_EXIT}, 400

    user = UserModel(user_name, password)
    user.save_to_db()

    return {"message": USER_OP.format("created")}, 201


@user.route('/delete', methods=['POST'])
def delete():
    user_id = request.values['userId']
    user = UserModel.find_by_id(user_id)
    if not user:
        return {"message": USER_NOT_FOUND}, 404
    user.delete_from_db()
    return {"message": USER_OP.format("deleted")}, 200


@user.route('/login',method=['POST'])
def login():
    user_name = request.values['userName']
    password = request.values['password']
    user = UserModel.find_by_username(user_name)
    if user and safe_str_cmp(user.password, password):
        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(user.id)
        return {"access_token": access_token, "refresh_token": refresh_token}, 200
    return {"message": "Invalid credentials!"}, 401


@user.route('/logout',method=['POST'])
@jwt_required
def logout():
    jti = get_raw_jwt()["jti"]
    user_id = get_jwt_identity()
    BLACKLIST.add(jti)
    return {"message": USER_LOG_OUT.format(user_id)}, 200


@user.route('/refresh',method=['POST'])
@jwt_refresh_token_required
def Refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user, fresh=False)
    return {"access_token": new_token}, 200