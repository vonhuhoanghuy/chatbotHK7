from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import os
import random
import nltk
import numpy as np
import pickle
from tensorflow.keras.models import load_model
import ssl
from bson import ObjectId
from flask import jsonify
from bson.json_util import dumps
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_default_secret_key')
client = MongoClient('mongodb://localhost:27017/chatbot_users')
db = client.get_database('chatbot_users')
users_collection = db.users


try:
    nltk.download('punkt')
    nltk.download('wordnet')
    lemmatizer = nltk.WordNetLemmatizer()
    model = load_model('models/chatbot_model.h5')
    words = pickle.load(open('models/words.pkl', 'rb'))
    classes = pickle.load(open('models/classes.pkl', 'rb'))

    with open('data.json', 'r', encoding='utf-8') as file:
        intents = json.load(file)

    logger.info("Đã tải xong mô hình và dữ liệu chatbot.")
except Exception as e:
    logger.error(f"Lỗi khi tải mô hình và dữ liệu: {str(e)}")
    raise
def clean_up_sentence(sentence):
    """Tiền xử lý câu đầu vào"""
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence, words):
    """Chuyển đổi câu thành bag of words"""
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, word in enumerate(words):
            if word == s:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    """Dự đoán intent của câu đầu vào"""
    bow = bag_of_words(sentence, words)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return [{"intent": classes[r[0]], "probability": str(r[1])} for r in results]

def get_response(intents_list):
    """Lấy câu trả lời dựa trên intent dự đoán được"""
    if not intents_list:
        return "Xin lỗi, tôi không hiểu câu hỏi của bạn. Bạn có thể diễn đạt lại không?"
    tag = intents_list[0]['intent']
    for intent in intents['intents']:
        if intent['tag'] == tag:
            return random.choice(intent['responses'])
    return "Xin lỗi, tôi không thể trả lời câu hỏi này."

def log_conversation(user_message, bot_response, intent=None):
    """Ghi log cuộc hội thoại"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} | User: {user_message} | Bot: {bot_response} | Intent: {intent}\n"
    with open('conversation_logs.txt', 'a', encoding='utf-8') as f:
        f.write(log_entry)
        
        
        
        
@app.route('/')
def home():
    return "Welcome to Flask Chatbot API"

@app.route('/api/get_response', methods=['POST'])
def get_bot_response():
    """API xử lý tin nhắn từ ReactJS"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({"response": "Vui lòng nhập tin nhắn"}), 400
        intents_list = predict_class(user_message)
        response = get_response(intents_list)
        intent = intents_list[0]['intent'] if intents_list else 'unknown'
        log_conversation(user_message, response, intent)
        return jsonify({"response": response, "intent": intent}), 200
    except Exception as e:
        logger.error(f"Lỗi khi xử lý tin nhắn: {str(e)}")
        return jsonify({"response": "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau."}), 500

@app.route('/api/register', methods=['POST'])
def register_user():
    """API đăng ký người dùng"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"message": "Tên đăng nhập và mật khẩu là bắt buộc"}), 400

        if users_collection.find_one({"username": username}):
            return jsonify({"message": "Tên đăng nhập đã tồn tại"}), 409

        hashed_password = generate_password_hash(password)
        users_collection.insert_one({"username": username, "password": hashed_password})
        return jsonify({"message": "Đăng ký thành công"}), 201
    except Exception as e:
        logger.error(f"Lỗi khi đăng ký: {str(e)}")
        return jsonify({"message": "Đã xảy ra lỗi"}), 500

@app.route('/api/login', methods=['POST'])
def login_user():
    """API đăng nhập người dùng"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"message": "Tên đăng nhập và mật khẩu là bắt buộc"}), 400
        user = users_collection.find_one({"username": username})
        if not user or not check_password_hash(user['password'], password):
            return jsonify({"message": "Tên đăng nhập hoặc mật khẩu không chính xác"}), 401

        return jsonify({"message": "Đăng nhập thành công", "user": {"username": username, "user_id": str(user['_id'])}}), 200
    except Exception as e:
        logger.error(f"Lỗi khi đăng nhập: {str(e)}")
        return jsonify({"message": "Đã xảy ra lỗi"}), 500

@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    """API tạo mới một cuộc trò chuyện"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({"message": "User ID là bắt buộc"}), 400

        try:
            user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        except Exception:
            return jsonify({"message": "User ID không hợp lệ"}), 400

        conversation = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "title": "Trò chuyện với chatbot N5",
            "messages": []
        }
        result = db.conversations.insert_one(conversation)

        conversations = list(
            db.conversations.find({"user_id": user_id}, {"_id": 1, "title": 1, "created_at": 1})
        )
        for conversation in conversations:
            conversation["_id"] = str(conversation["_id"])

        return jsonify({
            "message": "Cuộc trò chuyện đã được tạo",
            "conversation_id": str(result.inserted_id),
            "conversations": conversations
        }), 201

    except Exception as e:
        logger.error(f"Lỗi khi tạo cuộc trò chuyện: {str(e)}")
        return jsonify({"message": "Đã xảy ra lỗi"}), 500


@app.route('/api/conversations/<conversation_id>/messages', methods=['POST'])
def add_message(conversation_id):
    """API thêm tin nhắn vào cuộc trò chuyện"""
    try:
        data = request.get_json()
        sender = data.get('sender')  
        message = data.get('message')

        if not sender or not message:
            return jsonify({"message": "Sender và message là bắt buộc"}), 400
        

        conversation_id = ObjectId(conversation_id)

        message_data = {
            "sender": sender,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        result = db.conversations.update_one(
            {"_id": conversation_id},
            {"$push": {"messages": message_data}}
        )
        
        if result.matched_count == 0:
            return jsonify({"message": "Không tìm thấy cuộc trò chuyện"}), 404

        return jsonify({"message": "Tin nhắn đã được thêm"}), 200
    except Exception as e:
        logger.error(f"Lỗi khi thêm tin nhắn: {str(e)}")
        return jsonify({"message": "Đã xảy ra lỗi"}), 500



@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """API lấy danh sách các cuộc trò chuyện"""
    try:
        user_id = request.args.get('user_id')
        print(f"Received user_id: {user_id}")
        
        if not user_id:
            return jsonify({"message": "User ID là bắt buộc"}), 400


        user_id = ObjectId(user_id)

        conversations = list(db.conversations.find({"user_id": user_id}, {"messages": 0}))
        print(conversations)


        for conversation in conversations:
            conversation["_id"] = str(conversation["_id"])
            conversation["user_id"] = str(conversation["user_id"])

        return jsonify({"conversations": conversations}), 200
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách cuộc trò chuyện: {str(e)}")
        return jsonify({"message": "Đã xảy ra lỗi"}), 500
from bson import ObjectId

@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation_detail(conversation_id):
    """API lấy chi tiết một cuộc trò chuyện"""
    try:
        conversation_id = ObjectId(conversation_id)

        conversation = db.conversations.find_one({"_id": conversation_id})
        if not conversation:
            return jsonify({"message": "Không tìm thấy cuộc trò chuyện"}), 404

        conversation = json.loads(dumps(conversation))

        return jsonify({"conversation": conversation}), 200

    except Exception as e:
        logger.error(f"Lỗi khi lấy chi tiết cuộc trò chuyện: {str(e)}")
        return jsonify({"message": "Đã xảy ra lỗi"}), 500
if __name__ == '__main__':
    app.run(debug=True)
