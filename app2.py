from flask import Flask, render_template, request, jsonify
import jwt
from pymongo import MongoClient
from datetime import datetime, timedelta
app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.junglemini  # 'dbjungle'라는 이름의 db를 만들거나 사용합니다.
articles = db.articles
users = db.users

SECRET_KEY = 'jungleboard'

# http://localhost:5000
@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/login')
def login():
    payload = {
        'email': "a44121078@gmail.com",
        'exp': datetime.utcnow() + timedelta(seconds=300)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return render_template('index.html', token = token)

@app.route('/home')
def home():
    token = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        article_list = list(articles.find({}, {'_id': False}))
        article_like_list = list(articles.find({}, {'_id': False}).sort("like", -1))

        for article in article_list:
            article_date_str = article['date']
            article_date = datetime.strptime(article_date_str, '%Y-%m-%d %H:%M:%S')
            article['date'] = article_date
        article_new_list = sorted(article_list, key=lambda x: x['date'])

        ranking_names = []
        
        cursor = list(users.find({}, {'articles': 1}))
        cursor.sort(key=lambda x: len(x['articles']), reverse=True)
        count = 0
        for user in cursor:
            print(user['_id'])
            ranking_names.append(users.find_one({'_id':user['_id']})['nickname'])
            count += 1
            if count == 3:
                break

        return render_template('home.html', article_new_list = article_new_list, article_like_list = article_like_list, ranking_names = ranking_names)
    except jwt.ExpiredSignatureError:
        return "ExpiredSignatureError"
    except jwt.exceptions.DecodeError:
        return "exceptions.DecodeError"

@app.route('/profile/<category>')
def profile(category):
    token = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_name = users.find_one({'email': payload['email']}, {'_id': False})["nickname"]
        # 사용자가 쓴 article list
        write_list = list(articles.find({'nickname': user_name}))

        cursor2 = list(users.find({}, {'likes': 1}))
        for user in cursor2:
            if user['nickname'] == user_name: # 현재 사용자 id와 맞는 글들의 id 리스트 가져옴
                like_id_list = user['likes'] #list
                # id_list를 가지고 실제 like_list를 가져와야 함
                break

        like_list = []

        for id in like_id_list:
            like = articles.find_one({'_id': id}, {'_id': False})
            if like is not None:
                like_list.append(like)

        # # 현재 사용자 id를 가져옴
        # print(payload['_id']) 
        # now_user_id = payload['_id']

        # cursor1 = list(users.find({}, {'writes': 1}))
        # for user in cursor1:
        #     if user['_id'] == now_user_id: # 현재 사용자 id와 맞는 글들의 id 리스트 가져옴
        #         write_id_list = user['writes'] #list
        #         # id_list를 가지고 실제 write_list를 가져와야 함
        #         break

        # write_list = []

        # for id in write_id_list:
        #     write = articles.find_one({'_id': id}, {'_id': False})
        #     if write is not None:
        #         write_list.append(write)

        
        
        return render_template('profile.html', payload=payload, category=category)#, write_list=write_list, like_list=like_list)
    except jwt.ExpiredSignatureError:
        return render_template('index.html')
    except jwt.exceptions.DecodeError:
        return render_template('index.html')


    cursor = list(users.find({}, {'writes': 1}))
    for user in cursor:
        print(user['writes'])

    #user_like_list = list(users.find({'좋아요글'}, {'_id': False}).sort("like", 1))
    #user_write_list = list(users.find({'내가쓴글'}, {'_id': False}).sort("like", -1))
    return render_template('profile.html', category = category)#, user_like_list = user_like_list, user_write_list = user_write_list)


if __name__ == '__main__':  
   app.run('0.0.0.0',port=5000,debug=True)