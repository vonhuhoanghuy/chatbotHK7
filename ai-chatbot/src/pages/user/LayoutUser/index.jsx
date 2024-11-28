import { memo, useState } from "react";
import ChatApp from "../ChatApp";
import "./style.scss";
import Sidebar from "../SideBar";

const LayoutUser = () => {
  const [selectedChat, setSelectedChat] = useState(null);
  const [messages, setMessages] = useState([]);

  const handleSelectChat = (chatId) => {
    const conversation_id = chatId;

    fetch(`http://127.0.0.1:5000/api/conversations/${conversation_id}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json"
      }
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.conversation) {
          setSelectedChat(data.conversation);
          setMessages(data.conversation.messages || []);
        } else {
          console.error("Lỗi khi lấy cuộc trò chuyện:", data.message);
        }
      })
      .catch((error) => {
        console.error("Lỗi khi gửi yêu cầu:", error);
      });
  };

  return (
    <div className="container">
      <div className="row">
        <div className="col-lg-3">
          <Sidebar onSelectChat={handleSelectChat} />
        </div>
        <div className="col-lg-9">
          <ChatApp chat={selectedChat} initialMessages={messages} />
        </div>
      </div>
    </div>
  );
};

export default memo(LayoutUser);
