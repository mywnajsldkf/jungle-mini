from flask import Flask, render_template, jsonify, request
import requests
from pymongo import MongoClient
app = Flask(__name__)

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.junglemini  # 'dbjungle'라는 이름의 db를 만들거나 사용합니다.

# # http://localhost:5000/home
@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/profile/<list_category>')
def profile(list_category):
    print(list_category)
    return render_template('profile.html', category_name = list_category)

@app.route('/home/newest', methods=['GET'])
def read_newest():
    # 최신순으로 정렬하고 넘겨준다.
    result = list(db.articles.find({}, {'_id': False}).sort('like', 1))
    return jsonify({'result': 'success', 'articles': result})

@app.route('/home/favorite', methods=['GET'])
def read_favorite():
    # 좋아요순으로 정렬하고 넘겨준다.
    result = list(db.articles.find({}, {'_id': False}).sort('like', -1))
    return jsonify({'result': 'success', 'articles': result})

@app.route('/home/ranking', methods=['GET'])
def read_ranking():
    # 작성글순으로 정렬하고 넘겨준다.
    result = list(db.users.find({}, {'_id': False}).sort('articlenum', -1))
    return jsonify({'result': 'success', 'articles': result})

@app.route('/login')
def go_login():
    return render_template('login.html')

# @app.route('/mypage')
# def mypage():
#     return render_template('mypage.html')


if __name__ == '__main__':  
   app.run('0.0.0.0',port=5000,debug=True)


# 좋아요, 내가 쓴 글 가져오기
# 페이지 단위

# article1 = {"articleclass": "study", "title": "1번", "like": 1}
    # article2 = {"articleclass": "communication", "title": "2번", "like": 2}
    # article3 = {"articleclass": "lifeinfo", "title": "3번", "like": 3}
    # article4 = {"articleclass": "study", "title": "4번", "like": 4}
    # article5 = {"articleclass": "communication", "title": "5번", "like": 5}
    # article6 = {"articleclass": "lifeinfo", "title": "6번", "like": 6}
    # article7 = {"articleclass": "study", "title": "7번", "like": 7}
    # article8 = {"articleclass": "communication", "title": "8번", "like": 8}
    # article9 = {"articleclass": "lifeinfo", "title": "9번", "like": 9}
    # db.articles.insert_one(article1)
    # db.articles.insert_one(article2)
    # db.articles.insert_one(article3)
    # db.articles.insert_one(article4)
    # db.articles.insert_one(article5)
    # db.articles.insert_one(article6)
    # db.articles.insert_one(article7)
    # db.articles.insert_one(article8)
    # db.articles.insert_one(article9)