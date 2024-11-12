import json
import random
import numpy as np
import pickle
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
import tkinter as tk
from tkinter import scrolledtext

# Tải các gói dữ liệu cần thiết
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Tải mô hình và dữ liệu đã lưu
model = load_model('./models/chatbot_model.h5')
words = pickle.load(open('./models/words.pkl', 'rb'))
classes = pickle.load(open('./models/classes.pkl', 'rb'))

# Tải dữ liệu từ file data.json
lemmatizer = WordNetLemmatizer()
with open('data.json', 'r', encoding='utf-8') as file:
    intents_data = json.load(file)

# Hàm để chuyển đổi câu hỏi từ người dùng thành dạng mà mô hình có thể xử lý
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence, words):
    bag = [0] * len(words)
    sentence_words = clean_up_sentence(sentence)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence, words)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def get_response(intents_list, intents_data):
    if intents_list:
        intent = intents_list[0]['intent']
        for i in intents_data['intents']:
            if i['tag'] == intent:
                response = random.choice(i['responses'])
                return response
    return "Xin lỗi, tôi không hiểu câu hỏi của bạn."



def chatbot_response(user_input):
    intents = predict_class(user_input)
    response = get_response(intents, intents_data)
    return response


print("Chatbot đang hoạt động! (Gõ 'exit' để thoát)")
while True:
    user_input = input("Bạn: ")
    if user_input.lower() == 'exit':
        break
    intents = predict_class(user_input)
    response = get_response(intents, intents_data) # Pass intents_data to get_response
    print("Chatbot:", response)


# Giao diện chatbot
def send_message():
    user_message = user_input.get()
    if user_message:
        chat_window.insert(tk.END, "Bạn: " + user_message + "\n")
        intents = predict_class(user_message)
        response = get_response(intents, intents_data)
        chat_window.insert(tk.END, "Chatbot: " + response + "\n\n")
        user_input.delete(0, tk.END)

# Thiết lập giao diện
root = tk.Tk()
root.title("Chatbot")
root.geometry("400x500")

chat_window = scrolledtext.ScrolledText(root, state='normal', wrap=tk.WORD, bg="light grey")
chat_window.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

user_input = tk.Entry(root, width=50)
user_input.pack(pady=10)

send_button = tk.Button(root, text="Gửi", command=send_message)
send_button.pack(pady=10)

root.mainloop()






# from flask import Flask, request, jsonify
# from chatbot_learning import ChatbotLearning
# from external_apis import ExternalAPIs
# from database import Database

# app = Flask(__name__)
# db = Database()
# chatbot_learning = ChatbotLearning(db)
# external_apis = ExternalAPIs()

# @app.route('/api/chat', methods=['POST'])
# async def chat():
#     data = request.json
#     user_input = data.get('message')
    
#     # Xử lý input và get response
#     response = process_input(user_input)
    
#     # Log conversation để học
#     chatbot_learning.log_conversation(
#         user_input=user_input,
#         bot_response=response['message'],
#         intent=response['intent']
#     )
    
#     # Nếu cần thông tin external
#     if response['intent'] == 'weather':
#         weather_data = await external_apis.get_weather(response['city'])
#         response['additional_data'] = weather_data
    
#     return jsonify(response)

# @app.route('/api/feedback', methods=['POST'])
# def feedback():
#     data = request.json
#     chatbot_learning.learn_from_feedback(
#         conversation_id=data['conversation_id'],
#         is_helpful=data['is_helpful']
#     )
#     return jsonify({'status': 'success'})