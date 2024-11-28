import React, { useContext, useState, useEffect, useRef } from "react";
import "./styleChatApp.scss";
import { BiSolidMicrophone } from "react-icons/bi";

import { UserContext } from "../../../middleware/UserContext";
import VoiceChat from "../VoiceChat/index.js";
const ChatApp = ({ chat, initialMessages }) => {
  const { user } = useContext(UserContext);
  const nameUser = user?.username;

  const [messages, setMessages] = useState([
    {
      id: 1,
      text: `👋 Xin chào ${nameUser} ! Tôi có thể giúp gì cho bạn?`,
      isUser: false
    }
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const statusSpanRef = useRef(null);
  const voiceChatRef = useRef(null);

  useEffect(() => {
    if (initialMessages.length > 0) {
      setMessages(
        initialMessages.map((msg) => ({
          id: msg._id || Date.now(),
          text: msg.message,
          isUser: msg.sender === nameUser
        }))
      );
    } else {
      setMessages([
        {
          id: 1,
          text: `👋 Xin chào ${nameUser} ! Tôi có thể giúp gì cho bạn?`,
          isUser: false
        }
      ]);
    }
  }, [initialMessages, nameUser]);

  useEffect(() => {
    voiceChatRef.current = new VoiceChat(
      handleVoiceInput,
      statusSpanRef.current
    );
  }, []);

  const handleVoiceInput = (text) => {
    setInputValue(text);
    sendMessage(text);
  };

  const sendMessage = async (message) => {
    if (!message.trim()) return;

    const userMessage = { id: Date.now(), text: message, isUser: true };

    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInputValue("");
    setIsTyping(true);
    const conversation_id = chat?._id?.$oid;

    try {
      const response = await fetch("http://127.0.0.1:5000/api/get_response", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
      });
      const data = await response.json();

      await fetch(
        `http://127.0.0.1:5000/api/conversations/${conversation_id}/messages`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            sender: nameUser,
            message: message
          })
        }
      );

      await fetch(
        `http://127.0.0.1:5000/api/conversations/${conversation_id}/messages`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            sender: "bot",
            message: data.response
          })
        }
      );

      setMessages((prevMessages) => [
        ...prevMessages,
        { id: Date.now(), text: data.response, isUser: false }
      ]);
    } catch (error) {
      console.error("Lỗi khi gửi tin nhắn:", error);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") sendMessage(inputValue);
  };

  const startVoiceRecognition = () => {
    voiceChatRef.current?.startRecording();
  };

  return (
    <div className="chat-app">
      <div className="chat-main">
        <div className="chat-container">
          <div className="chat-content">
            {messages.map((message, key) => (
              <div
                key={key}
                className={`chat-message ${
                  message.isUser ? "user-message" : "bot-message"
                }`}
              >
                {message.text}
              </div>
            ))}
            {isTyping && (
              <div className="chat-message bot-message">...Đang trả lời</div>
            )}
          </div>
          <div className="chat-input-area">
            <input
              type="text"
              placeholder="Nhập tin nhắn..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              className="chat-input"
            />
            <button
              onClick={() => sendMessage(inputValue)}
              className="chat-button"
            >
              Gửi
            </button>
            <button onClick={startVoiceRecognition} className="chat-mic-button">
              <BiSolidMicrophone />
            </button>
          </div>
          <span ref={statusSpanRef} className="recording-status"></span>
        </div>
      </div>
    </div>
  );
};

export default ChatApp;
