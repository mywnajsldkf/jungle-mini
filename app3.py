import bson.json_util as json_util
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client.jungle      # database 이름: jungle
articles = db.article   # collection 이름: article
counters = db.count     # collection 이름: count

@app.route("/")
def hello_world():
    '''
    article = {
        '_id': 'userId',
        'seq': 0
    }

    counters.insert_one(article)
    '''
    # print(articles.find_one())
    return render_template('index.html')

@app.route("/write", methods=['GET'])
def getEditor():
    return render_template('write.html')

@app.route("/article/<articleId>", methods=['GET'])
def getArticle(articleId):
    # result = json_util.dumps(articles.find_one({'_id':ObjectId(articleId)}))
    result = json.dumps(articles.find_one({'_id':ObjectId(articleId)}, {'_id': False}), ensure_ascii=False)
    print(result)
    return jsonify({'result': 'success', 'article': result})
    # print(result)
    # return jsonify({'result':'success','article':result})

@app.route("/write", methods=['POST'])
def writeArticle():
    title_receive = request.form['title_give']
    category_receive = request.form['category_give']
    content_receive = request.form['content_give']

    # article_id = getNextSequence(title_receive)
    article = {'title': title_receive,
            'category': category_receive,
            'content': content_receive, 
            'date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'nickname': 'token',
            'like': 0
            }
    articles.insert_one(article)

    return jsonify({'result': 'success'})

'''
def getNextSequence(title):
    a = counters.find_one_and_update(
        {"_id": title}, {"$inc": {"sequence_value":1}}, new=True
    )
    print(a)
'''

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)