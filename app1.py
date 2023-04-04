from pymongo import MongoClient
from flask import Flask, render_template, request, flash, jsonify, redirect, url_for, session
from bson.objectid import ObjectId
from datetime import timedelta

client = MongoClient('localhost', 27017)
db = client.junglelife
user = db.user
article = db.article

app = Flask(__name__)
app.secret_key = 'secretkey'
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=10)

@app.route('/home')
def home():
    # if session.get("id") is None:
    #     상단에 마이페이지, 로그아웃
    # else:
    #     상단에 로그인
    return "Hello"

@app.route('/join', methods=["GET", "POST"])
def user_join():
    if request.method == "POST":
        receive_email = request.form.get("email", type=str)
        receive_password1 = request.form.get("password1", type=str)
        receive_password2 = request.form.get("password2", type=str)
        receive_nickname = request.form.get("nickname", type=str)
        
        user_email = user.find_one({"email":receive_email})
        user_nickname = user.find_one({"nickname":receive_nickname})

        if user_email is not None:
            flash("이미 존재하는 이메일입니다.")
            return render_template("join.html")
        
        if user_nickname is not None:
            flash("이미 존재하는 닉네임입니다.")
            return render_template("join.html")

        if receive_email == "" or receive_password1 == "" or receive_password2 == "" or receive_nickname == "":
            flash("입력되지 않은 값이 있습니다.")
            return render_template("join.html")
    
        if len(receive_password1)<8 or len(receive_password1)>20:
            flash("비밀번호는 8자~20자 이내로 입력해주세요.")
            return render_template("join.html")
        if receive_password1 != receive_password2:
            flash("비밀번호가 일치하지 않습니다.")
            return render_template("join.html")
        
        post = {
            "email":receive_email,
            "password":receive_password1,
            "nickname":receive_nickname
        }
        user.insert_one(post)
        return redirect(url_for("home"))
    else:
        return render_template("join.html")
    
@app.route('/login', methods=["GET","POST"])
def user_login():
    if request.method == "POST":
        receive_email = request.form.get("email")
        receive_pass=request.form.get("password")
        
        data = user.find_one({"email":receive_email})
        if data is None:
            flash("회원정보가 없습니다.") 
            return redirect(url_for("user_login"))
        else:
            if data.get("password") == receive_pass:
                session["email"] = receive_email
                session["name"] = data.get("name")
                session["id"] = str(data.get("_id"))
                # 세션 유지시간은 default 값이 있지만, 임의로 설정하기 위해 permanent 값 줌
                session.permanent = True
                return redirect(url_for("home"))
            else:
                flash("비밀번호가 틀립니다.")
                return redirect(url_for("user_login"))
    else:
        return render_template("login.html")
    
# @app.route('/login2', methods=["POST"])
# def user_login2():


@app.route('/validate/email', methods=["POST"])
def email_validate():
    receive_email = request.form['email_give']
    data = user.find_one({"email":receive_email})
    if data is None:
        return jsonify({'result': 'success', 'msg': '사용가능한 이메일입니다.'})
    else:
        return jsonify({'result':'fail','msg':'이미 존재하는 이메일입니다.'})
    
@app.route('/validate/nickname', methods=["POST"])
def nickname_validate():
    receive_nickname = request.form['nickname_give']
    data = user.find_one({"nickname":receive_nickname})
    if data is None:
        return jsonify({'result': 'success', 'msg': '사용가능한 닉네임입니다.'})
    else:
        return jsonify({'result':'fail','msg':'이미 존재하는 닉네임입니다.'})

if __name__ == '__main__':  
   app.run(host='0.0.0.0',port=5000,debug=True)