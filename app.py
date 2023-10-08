import base64
import http
import json

import requests as requests
from bson import json_util
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

MONGODB_URL = "mongodb+srv://nadi:Nadi123@myflix-cluster.qgxfauc.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGODB_URL)
db = client["student"]
collection = db["user"]


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


@app.route("/user", methods=['POST'])
def user():
    if request.method == 'POST':
        req_json = request.json
        usr = req_json["username"]
        pWordNew = req_json["password"]
        post = {"userName": usr, "passWord": pWordNew}
        collection.insert_one(post)
    return "Signup Sucessfull"


@app.route("/profile")
def profile():
    #all_users = list(collection.find())
    all_users = get_data()
    json_data = json.loads(all_users)
    return render_template("profile.html", users=json_data)


def get_data():
    conn = http.client.HTTPConnection("127.0.0.1", 5000)
    payload = ''
    headers = {}
    conn.request("GET", "/viewdata", payload, headers)
    res = conn.getresponse()
    data = res.read()
    data.decode("utf-8")

    return data.decode("utf-8")


@app.route('/delete/<user_name>', methods=['POST'])
def delete_user(user_name):
    collection.delete_one({'userName': user_name})
    return redirect(url_for('profile'))


@app.route("/viewdata")
def viewData():
    all_users = list(collection.find())
    return json.loads(json_util.dumps(all_users))


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
    #decode_data = base64.b64decode(data_url)
    return data_url


@app.route('/test2', methods=['POST'])
def test2():
    pname = request.form['user']
    return render_template('test2.html', myname=pname)


if __name__ == "__main__":
    app.run(debug=True)
