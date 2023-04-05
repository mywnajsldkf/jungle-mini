from pymongo import MongoClient
from flask import Flask, render_template, request, flash, jsonify, redirect, url_for, session
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import jwt


client = MongoClient('localhost', 27017)
db = client.junglelife
user = db.user
article = db.article
SECRET_KEY = 'jungleboard'

app = Flask(__name__)

# app.secret_key = 'secretkey'
# app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=10)

@app.route('/home')
def hello_world():
    return render_template("home.html")

@app.route("/search", methods=["POST"])
def keyword_search():
    keyword_receive = request.form.get("keyword")
    search_list = [{'title':{'$regex':keyword_receive}},{'content':{'$regex':keyword_receive}},{'nickname':{'$regex':keyword_receive}}]
    datas =article.find({'$or':search_list})
    return render_template("view.html", datas= list(datas))

@app.route('/join', methods=["GET", "POST"])
def user_join():
    if request.method == "POST":   
        email_receive = request.form["email_give"]
        password1_receive = request.form["password1_give"]
        password2_receive = request.form["password2_give"]
        nickname_receive = request.form["nickname_give"]
        
        user_email = user.find_one({"email":email_receive})
        user_nickname = user.find_one({"nickname":nickname_receive})

        if user_email is not None:
            return jsonify({'result': 'fail', 'msg':'이미 존재하는 이메일입니다.'})
        
        if user_nickname is not None:
            return jsonify({'result': 'fail', 'msg':'이미 존재하는 닉네임입니다.'})

        if email_receive == "" or password1_receive == "" or password2_receive == "" or nickname_receive == "":
            return jsonify({'result': 'fail', 'msg':'입력되지 않은 값이 있습니다.'})
    
        if len(password1_receive)<8 or len(password1_receive)>20:
            return jsonify({'result': 'fail', 'msg':'비밀번호는 8~20자 이내로 입력해주세요.'})

        if password1_receive != password2_receive:
            return jsonify({'result': 'fail', 'msg':'비밀번호가 일치하지 않습니다.'})
        
        post = {
            "email":email_receive,
            "password":password1_receive,
            "nickname":nickname_receive
        }
        user.insert_one(post)
        return jsonify({'result': 'success', 'msg':'회원가입 성공'})
    else:
        return render_template("join.html")

    
@app.route('/login', methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email_receive = request.form['email_give']
        password_receive=request.form['password_give']
        
        data = user.find_one({'email':email_receive})
        if data is not None:
            if data["password"] == password_receive:
                payload = {
                    'email': email_receive,
                    'exp': datetime.utcnow() + timedelta(seconds=300)
                }
                token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
                return jsonify({'result': 'success', 'usertoken':token})
            else:
                return jsonify({'result': 'fail', 'msg':'비밀번호가 틀립니다.'})
        else: 
            return jsonify({'result':'fail', 'msg':'회원정보가 없습니다.'})
    else:
        return render_template("login.html")

@app.route('/validate/email', methods=["POST"])
def email_validate():
    receive_email = request.form['email_give']
    data = user.find_one({"email":receive_email})
    if data is None and receive_email != "":
        return jsonify({'result': 'success', 'msg': '사용할 수 있는 이메일입니다.'})
    else:
        return jsonify({'result':'fail','msg':'사용할 수 없는 이메일입니다.'})
    
@app.route('/validate/nickname', methods=["POST"])
def nickname_validate():
    receive_nickname = request.form['nickname_give']
    data = user.find_one({"nickname":receive_nickname})
    if data is None and receive_nickname !="":
        return jsonify({'result': 'success', 'msg': '사용할 수 있는 닉네임입니다.'})
    else:
        return jsonify({'result':'fail','msg':'사용할 수 없는 닉네임입니다.'})

if __name__ == '__main__':  
   app.run(host='0.0.0.0',port=5000,debug=True)
