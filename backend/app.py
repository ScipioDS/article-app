from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import os

app = Flask(__name__)
CORS(app)

# MongoDB connection
mongo_host = os.getenv('MONGO_HOST', 'mongodb')
client = MongoClient(f'mongodb://{mongo_host}:27017/')
db = client.articles_db
articles_collection = db.articles

@app.route('/articles', methods=['GET'])
def get_articles():
    articles = []
    for article in articles_collection.find().sort('created_at', -1):
        article['id'] = str(article['_id'])
        del article['_id']
        articles.append(article)
    return jsonify(articles)

@app.route('/articles/<article_id>', methods=['GET'])
def get_article(article_id):
    article = articles_collection.find_one({'_id': ObjectId(article_id)})
    if article:
        article['id'] = str(article['_id'])
        del article['_id']
        return jsonify(article)
    return jsonify({'error': 'Article not found'}), 404

@app.route('/articles', methods=['POST'])
def create_article():
    data = request.json
    article = {
        'title': data['title'],
        'content': data['content'],
        'author': data['author'],
        'created_at': datetime.utcnow().isoformat()
    }
    result = articles_collection.insert_one(article)
    return jsonify({'message': 'Article created successfully', 'id': str(result.inserted_id)}), 201


@app.route('/articles/<article_id>', methods=['PUT'])
def update_article(article_id):
    print(f"DEBUG: Received article_id: {article_id}")
    print(f"DEBUG: article_id type: {type(article_id)}")

    data = request.json
    print(f"DEBUG: Received data: {data}")

    try:
        object_id = ObjectId(article_id)
        print(f"DEBUG: Converted to ObjectId: {object_id}")
    except Exception as e:
        print(f"DEBUG: Error converting to ObjectId: {e}")
        return jsonify({'error': 'Invalid article ID format'}), 400

    update_data = {
        'title': data['title'],
        'content': data['content'],
        'author': data['author'],
        'updated_at': datetime.utcnow().isoformat()
    }

    print(f"DEBUG: Update data: {update_data}")

    result = articles_collection.update_one(
        {'_id': object_id},
        {'$set': update_data}
    )

    print(f"DEBUG: Update result - matched: {result.matched_count}, modified: {result.modified_count}")

    if result.matched_count:
        return jsonify({'message': 'Article updated successfully'})
    return jsonify({'error': 'Article not found'}), 404


@app.route('/articles/<article_id>', methods=['DELETE'])
def delete_article(article_id):
    result = articles_collection.delete_one({'_id': ObjectId(article_id)})
    if result.deleted_count:
        return jsonify({'message': 'Article deleted successfully'})
    return jsonify({'error': 'Article not found'}), 404

@app.route('/health')
def health_check():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)