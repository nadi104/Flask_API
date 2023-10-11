import base64
import http
import json
import os

import requests as requests
from bson import json_util
from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
import jwt
from functools import wraps

app = Flask(__name__)

SECRET_KEY = os.environ.get('SECRET_KEY') or 'this is a secret'
print(SECRET_KEY)
app.config['SECRET_KEY'] = SECRET_KEY

MONGODB_URL = "mongodb+srv://nadi:Nadi123@myflix-cluster.qgxfauc.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGODB_URL)
db = client["student"]
collection = db["user"]


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            usr_name = data.get('usr_name')
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        if not usr_name:
            jsonify({'error': 'No user name found'})
        return f(usr_name, *args, **kwargs)

    return decorated


@app.route("/generate_token")
def generate_token():
    try:
        name = request.json.get('usr_name')
        if not name:
            return {
                       "message": "Please provide user details",
                       "data": None,
                       "error": "Bad request"
                   }, 400
        # token_user = {"userName": data["usr_name"], "passWord": data["usr_password"]}
        token = jwt.encode({'usr_name': name}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})

    except Exception as e:
        return {
                   "message": "Something went wrong!!!..",
                   "error": str(e),
                   "data": None
               }, 500


@app.route("/")
def home():
    return render_template("home.html", name="Ashini")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/singin")
def singin():
    return render_template("singin.html")


@app.route("/register", methods=['POST'])
def register():
    if request.method == "POST":
        userName = request.form['user']
        passWord = request.form['password']
        post = {"userName": userName, "passWord": passWord}
        collection.insert_one(post)
        return "Sucessfully add new user!!!!...."
    else:
        return render_template("singin.html")


@app.route("/add_user", methods=['POST'])
@token_required
def add_user(usr_name):
    if request.method == 'POST':
        if usr_name == 'Ashini':
            req_json = request.json
            usr = req_json["username"]
            pWordNew = req_json["password"]
            post = {"userName": usr, "passWord": pWordNew}
            collection.insert_one(post)
            return "Signup Sucessfull"
        else:
            return jsonify({'error': 'Access denied'}), 403
    return "Cannot add the user"


@app.route("/profile")
def profile():
    # all_users = list(collection.find())
    all_users = get_data()
    json_data = json.dumps(all_users)
    return render_template("profile.html", users=json_data)


def get_data():
    conn = http.client.HTTPConnection("127.0.0.1", 5000)
    payload = ''
    headers = {}
    conn.request("GET", "/viewdata", payload, headers)
    res = conn.getresponse()
    data = res.read()
    # data.decode("utf-8")

    return data.decode("utf-8")


@app.route('/delete/<user_name>', methods=['POST'])
def delete_user(user_name):
    collection.delete_one({'userName': user_name})
    return redirect(url_for('profile'))


@app.route("/viewdata")
def viewData():
    all_users = list(collection.find())
    # mongo_all = json.loads(json_util.dumps(all_users))
    keep_users = []
    for new_user in all_users:
        u_name = new_user["userName"]
        u_passWord = new_user["passWord"]
        count = int(search_manypassword(u_passWord))
        if count > 1:
            u_passWord = u_passWord + " duplicate password"
        else:
            u_passWord = u_passWord
        keep_users.append({"userName": u_name, "passWord": u_passWord})
    return keep_users


@app.route("/searchpwd/<userpassword>")
def search_manypassword(userpassword):
    # password_duplicate = collection.find({"passWord": userpassword}, {"passWord": 1, "_id": False}).count_documents()
    password_duplicate = collection.count_documents({"passWord": userpassword})
    # return json.loads(json_util.dumps(password_duplicate))
    return str(password_duplicate)


@app.route('/update/<user_name>', methods=['GET', 'POST'])
def update_password(user_name):
    update_user = collection.find_one({'userName': user_name})
    if request.method == 'POST':
        new_password = request.form['password']
        data_to_pass = {
            'gust_username': user_name,
            'new_password': new_password
        }

        collection.update_one({'userName': user_name}, {'$set': {'passWord': new_password}})
        return redirect(url_for('profile'))

    return render_template('update.html', user=update_user)


@app.route('/password_update', methods=['POST'])
def update_mongo():
    if request.method == 'POST':
        req_json = request.json
        up_name = req_json['name']
        up_password = req_json['newPassword']
        collection.update_one({'userName': up_name}, {'$set': {'passWord': up_password}})
        return redirect(url_for('profile'))


@app.route('/test')
def test():
    data_url = get_data()
    # decode_data = base64.b64decode(data_url)
    return data_url


@app.route('/test2', methods=['POST'])
def test2():
    pname = request.form['user']
    return render_template('test2.html', myname=pname)


if __name__ == "__main__":
    app.run(debug=True)
