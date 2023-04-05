from flask import Flask, render_template, request
import jwt
from pymongo import MongoClient
from datetime import datetime, timedelta
app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

client = MongoClient('13.125.219.188', 27017, username="test", password="test")
db = client.junglelife
articles = db.article
users = db.user

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
        print(article_list)
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
        return render_template('index.html')
    except jwt.exceptions.DecodeError:
        return render_template('index.html')

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
                break

        like_list = []

        for id in like_id_list:
            like = articles.find_one({'_id': id}, {'_id': False})
            if like is not None:
                like_list.append(like)
        
        return render_template('profile.html', payload=payload, category=category, write_list=write_list, like_list=like_list)
    except jwt.ExpiredSignatureError:
        return render_template('index.html')
    except jwt.exceptions.DecodeError:
        return render_template('index.html')

if __name__ == '__main__':  
   app.run('0.0.0.0',port=5000,debug=True)