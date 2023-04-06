import bson.json_util as json_util
from flask import Flask, render_template, jsonify, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from jwt import encode, decode
import jwt
from pymongo import ReturnDocument
import config

app = Flask(__name__)
client = MongoClient('13.125.219.188', 27017, username="test", password="test")
db = client.junglelife      # database 이름: jungle
users = db.user
articles = db.article   # collection 이름: article
counters = db.count     # collection 이름: count
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

@app.route("/")
def hello():
    # TODO: articleId 사용하지 않고 하는 방법

    '''
    article = {
        '_id': 'articleId',
        'seq': 0
    }

    counters.insert_one(article)
    '''

    # print(articles.find_one())
    return redirect(url_for('home'))

@app.route('/islogin', methods=["GET"])
def islogin():
    token = request.cookies.get('mytoken')
    result = False
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=['HS256'])
        result = True
        return jsonify({'result': 'success', 'islogin': result})
    except jwt.ExpiredSignatureError:
        result = False
        return jsonify({'result': 'success', 'islogin': result})
    except jwt.exceptions.DecodeError:
        result = False
        return jsonify({'result': 'success', 'islogin': result})
    

@app.route('/home')
def home():
    token = request.cookies.get('mytoken')
    try:
        article_list = list(articles.find({}))
        article_like_list = list(articles.find({}).sort("like", -1))

        for article in article_list:
            article_date_str = article['date']
            article_date = datetime.strptime(article_date_str, '%Y-%m-%d %H:%M:%S')
            article['date'] = article_date
        article_new_list = sorted(article_list, key=lambda x: x['date'], reverse=True)

        ranking_names = []
        
        cursor = list(users.find({}, {'articles': 1}))
        cursor.sort(key=lambda x: len(x['articles']), reverse=True)
        count = 0
        # print(cursor)
        for u in cursor:
            # print(u['_id'])
            # ranking_names.append(u['_id'])
            ranking_names.append(users.find_one({'_id':u['_id']})['nickname'])
            count += 1
            if count == 3:
                break

        return render_template('home.html', article_new_list = article_new_list, article_like_list = article_like_list, ranking_names = ranking_names)
    except jwt.ExpiredSignatureError:
        return render_template('index.html')
    except jwt.exceptions.DecodeError:
        return render_template('index.html')

@app.route('/join', methods=["GET", "POST"])
def user_join():
    if request.method == "POST":   
        email_receive = request.form["email_give"]
        password1_receive = request.form["password1_give"]
        password2_receive = request.form["password2_give"]
        nickname_receive = request.form["nickname_give"]
        
        user_email = users.find_one({"email":email_receive})
        user_nickname = users.find_one({"nickname":nickname_receive})

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
            "nickname":nickname_receive,
            "likes":[],
            "articles":[]
        }
        users.insert_one(post)
        return jsonify({'result': 'success', 'msg':'회원가입 성공'})
    else:
        return render_template("join.html")

@app.route('/validate/email', methods=["POST"])
def email_validate():
    receive_email = request.form['email_give']
    data = users.find_one({"email":receive_email})
    if data is None and receive_email != "":
        return jsonify({'result': 'success', 'msg': '사용할 수 있는 이메일입니다.'})
    else:
        return jsonify({'result':'fail','msg':'사용할 수 없는 이메일입니다.'})
    
@app.route('/validate/nickname', methods=["POST"])
def nickname_validate():
    receive_nickname = request.form['nickname_give']
    data = users.find_one({"nickname":receive_nickname})
    if data is None and receive_nickname !="":
        return jsonify({'result': 'success', 'msg': '사용할 수 있는 닉네임입니다.'})
    else:
        return jsonify({'result':'fail','msg':'사용할 수 없는 닉네임입니다.'})

@app.route('/login', methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email_receive = request.form['email_give']
        password_receive=request.form['password_give']
        
        data = users.find_one({'email':email_receive})
        if data is not None:
            if data["password"] == password_receive:
                payload = {
                    'nickname': data["nickname"],
                    'exp': datetime.utcnow() + timedelta(seconds=3600) # TODO: 토큰!!! 시간 변경!
                }
                token = encode(payload, config.SECRET_KEY, algorithm='HS256')
                return jsonify({'result': 'success', 'usertoken':token})
            else:
                return jsonify({'result': 'fail', 'msg':'비밀번호가 틀립니다.'})
        else: 
            return jsonify({'result':'fail', 'msg':'회원정보가 없습니다.'})
    else:
        return render_template("login.html")

@app.route("/write", methods=['GET'])
def getEditor():
    return render_template('write.html')

@app.route("/article", methods=['GET'])
def getArticle():
    # 토큰
    token = request.cookies.get('mytoken')
    try:
        payload = decode(token, config.SECRET_KEY, algorithms=['HS256'])
        # print("payload: ", type(payload))
    except jwt.ExpiredSignatureError:
        return render_template('index.html')
    except jwt.exceptions.DecodeError:
        return render_template('index.html')

    return render_template('article.html', nickname = payload['nickname'])

# TODO: find_one Article ID로 수정하기
@app.route("/article/<articleId>", methods=['GET'])
def showArticle(articleId):
    result = articles.find_one({'_id':ObjectId(articleId)}, {'_id': False})
    return render_template('article.html', article = result)

@app.route("/board/<categoryId>")
def showBoard(categoryId):
    # result = list(articles.find({'category':categoryId}).limit(3))

    article_category_list = list(articles.find({'category':categoryId}))
    for article in article_category_list:
            article_date_str = article['date']
            article_date = datetime.strptime(article_date_str, '%Y-%m-%d %H:%M:%S')
            article['date'] = article_date
    result1 = sorted(article_category_list, key=lambda x: x['date'], reverse=True)
    result = [result1[0], result1[1], result1[2]]

    return render_template('board.html', board = result)

@app.route("/write", methods=['POST'])
def writeArticle():
    # 토큰
    token = request.cookies.get('mytoken')
    try:
        payload = decode(token, config.SECRET_KEY, algorithms=['HS256'])
        # print("payload: ", type(payload))
    except jwt.ExpiredSignatureError:
        return render_template('index.html')
    except jwt.exceptions.DecodeError:
        return render_template('index.html')

    title_receive = request.form['title_give']
    category_receive = request.form['category_give']
    content_receive = request.form['content_give']

    articleId = getNextSequence('articleId')
    article = {'title': title_receive,
            'category': category_receive,
            'content': content_receive, 
            'date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'nickname': payload['nickname'],
            'like': 0,
            'articleId': articleId
            }
    articles.insert_one(article)

    # TODO: 사용자의 articles에 article id를 추가한다.
    writeUser = users.find_one({'nickname': payload['nickname']})
    writeUser['articles'].append(article['articleId'])
    users.update_one({'nickname': payload['nickname']}, {'$set': {'articles': writeUser['articles']}})

    return jsonify({'result': 'success', 'category': category_receive})

def getNextSequence(title):
    a = counters.find_one_and_update(
        {"_id": title}, 
        {"$inc": {"seq":1}}, 
        return_document= ReturnDocument.AFTER
    )

    return(a['seq'])

@app.route('/article/like', methods=['POST'])
def likeArticle():
    # 토큰
    token = request.cookies.get('mytoken')
    try:
        payload = decode(token, config.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return render_template('index.html')
    except jwt.exceptions.DecodeError:
        return render_template('index.html')

    id_receive = request.form['id_give']

    article = articles.find_one({'_id': ObjectId(id_receive)})
    new_count = article['like'] + 1

    print(article['_id'])

    likeUser = users.find_one({'nickname': payload['nickname']})
    likeUser['likes'].append(article['_id'])

    print(likeUser['likes'])

    print(type(likeUser['likes']))
    articles.update_one({'_id': ObjectId(id_receive)}, {'$set': {'like': new_count}})
    users.update_one({'_id': ObjectId(likeUser['_id'])}, {'$set': {'likes': likeUser['likes']}})

    return jsonify({'result': 'success'})

@app.route('/profile/<category>')
def profile(category):
    token = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=['HS256'])
    
        user_name = users.find_one({'nickname': payload['nickname']})["nickname"]

        write_list = list(articles.find({'nickname': user_name}))

        cursor2 = list(users.find({'nickname': user_name}))
        for user in cursor2:
            # print(user)
            if user['nickname'] == user_name: # 현재 사용자 id와 맞는 글들의 id 리스트 가져옴
                like_id_list = user['likes'] #list
                break

        like_list = []

        for id in like_id_list:
            like = articles.find_one({'_id': id})
            if like is not None:
                like_list.append(like)
        print(like_list)
        print(write_list)
        
        return render_template('profile.html', payload=payload, category=category, write_list=write_list, like_list=like_list)
    except jwt.ExpiredSignatureError:
        return render_template('index.html')
    except jwt.exceptions.DecodeError:
        return render_template('index.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)