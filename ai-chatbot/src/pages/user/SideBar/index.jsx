import React, { useState, useEffect, useContext } from "react";
import "./style.scss";
import { UserContext } from "../../../middleware/UserContext";
import { BiBookAdd } from "react-icons/bi";
const Sidebar = ({ onSelectChat }) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  const { user } = useContext(UserContext);

  useEffect(() => {
    if (!user) return;

    const fetchConversations = async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `http://127.0.0.1:5000/api/conversations?user_id=${user?.user_id}`
        );
        const data = await response.json();
        setConversations(data.conversations);
      } catch (error) {
        console.error("Lỗi khi tải danh sách cuộc trò chuyện:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchConversations();
  }, [user]);

  const createNewConversation = async () => {
    if (!user) return;
    try {
      const response = await fetch("http://127.0.0.1:5000/api/conversations", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ user_id: user?.user_id })
      });
      const data = await response.json();
      setConversations(data.conversations);
    } catch (error) {
      console.error("Lỗi khi tạo cuộc trò chuyện:", error);
    }
  };

  const handleSelectConversation = (conversationId) => {
    setSelectedConversationId(conversationId);
    onSelectChat(conversationId);
  };

  return (
    <div className="sidebar">
      <div className="create-btn" onClick={createNewConversation}>
        <h2>Lịch sử ChatBot</h2>
        <BiBookAdd />
      </div>

      <div className="conversations-list">
        {loading ? (
          <p>Đang tải...</p>
        ) : (
          conversations?.map((conversation, key) => {
            console.log(conversation);
            return (
              <div
                key={key}
                className={`conversation-item ${
                  selectedConversationId === conversation?._id ? "selected" : ""
                }`}
                onClick={() => handleSelectConversation(conversation._id)}
              >
                {conversation?.title}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default Sidebar;
