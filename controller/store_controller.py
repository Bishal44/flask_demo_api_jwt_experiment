from flask import Blueprint

store = Blueprint("store", __name__)

@store.route('/show',methods=['GET'])
def show():
    return "hello"