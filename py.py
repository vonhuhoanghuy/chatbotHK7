from flask import Flask, render_template, request, jsonify
import json
import random
import numpy as np
import pickle
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
import os
import logging
from datetime import datetime

# Khởi tạo Flask app
app = Flask(__name__)

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tạo thư mục models nếu chưa tồn tại
if not os.path.exists('models'):
    os.makedirs('models')

try:
    # Tải các gói dữ liệu NLTK cần thiết
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('omw-1.4')
    nltk.download('punkt_tab')

    # Khởi tạo lemmatizer
    lemmatizer = WordNetLemmatizer()

    # Tải mô hình và dữ liệu
    model = load_model('models/chatbot_model.h5')
    words = pickle.load(open('models/words.pkl', 'rb'))
    classes = pickle.load(open('models/classes.pkl', 'rb'))
    
    # Tải dữ liệu intents
    with open('data.json', 'r', encoding='utf-8') as file:
        intents = json.load(file)

    logger.info("Đã tải xong mô hình và dữ liệu")

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
    try:
        # Tạo bag of words
        bow = bag_of_words(sentence, words)
        
        # Dự đoán thông qua mô hình
        res = model.predict(np.array([bow]))[0]
        
        # Lọc kết quả theo ngưỡng
        ERROR_THRESHOLD = 0.25
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
        
        # Sắp xếp theo xác suất
        results.sort(key=lambda x: x[1], reverse=True)
        
        return_list = [{"intent": classes[r[0]], "probability": str(r[1])} for r in results]
        return return_list

    except Exception as e:
        logger.error(f"Lỗi khi dự đoán class: {str(e)}")
        return []

def get_response(intents_list):
    """Lấy câu trả lời dựa trên intent dự đoán được"""
    try:
        if not intents_list:
            return "Xin lỗi, tôi không hiểu câu hỏi của bạn. Bạn có thể diễn đạt lại không?"

        tag = intents_list[0]['intent']
        list_of_intents = intents['intents']
        
        for intent in list_of_intents:
            if intent['tag'] == tag:
                result = random.choice(intent['responses'])
                return result

    except Exception as e:
        logger.error(f"Lỗi khi lấy response: {str(e)}")
        return "Xin lỗi, đã có lỗi xảy ra khi xử lý câu hỏi của bạn."
    

#"""Ghi log cuộc hội thoại"""
def log_conversation(user_message, bot_response, intent=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} | User: {user_message} | Bot: {bot_response} | Intent: {intent}\n"
    
    with open('conversation_logs.txt', 'a', encoding='utf-8') as f:
        f.write(log_entry)

@app.route('/')
def home():
    """Route cho trang chủ"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Lỗi khi render trang chủ: {str(e)}")
        return "Đã có lỗi xảy ra", 500

@app.route('/get_response', methods=['POST'])
def get_bot_response():
    """API endpoint để xử lý tin nhắn của người dùng"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"response": "Vui lòng nhập tin nhắn"})

        # Dự đoán intent
        ints = predict_class(user_message)
        
        # Lấy câu trả lời
        response = get_response(ints)
        
        # Log cuộc hội thoại
        intent = ints[0]['intent'] if ints else 'unknown'
        log_conversation(user_message, response, intent)
        
        return jsonify({"response": response})

    except Exception as e:
        logger.error(f"Lỗi khi xử lý tin nhắn: {str(e)}")
        return jsonify({
            "response": "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau."
        }), 500


# Tính năng phụ: API endpoint để lấy thống kê
@app.route('/stats', methods=['GET'])
def get_stats():
    """API endpoint để lấy thống kê về chatbot"""
    try:
        stats = {
            "total_intents": len(classes),
            "total_words": len(words),
            "total_patterns": sum(len(intent['patterns']) for intent in intents['intents']),
            "total_responses": sum(len(intent['responses']) for intent in intents['intents'])
        }
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Lỗi khi lấy thống kê: {str(e)}")
        return jsonify({"error": "Không thể lấy thống kê"}), 500

if __name__ == '__main__':
    app.run(debug=True)