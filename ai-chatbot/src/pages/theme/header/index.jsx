import React, { useContext } from "react";

import { useNavigate } from "react-router-dom";
import "./style.scss";
import { ROUTERS } from "../../../router/path";
import { UserContext } from "../../../middleware/UserContext";

const Header = () => {
  const navigator = useNavigate();
  const { user } = useContext(UserContext);
  const handleNavigator = (path) => {
    navigator(path);
  };
  const handleLogOut = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigator(ROUTERS.LOGIN);
  };

  return (
    <header className="chat-header">
      <h1 className="chat-title">Chat Bot Nhóm 5 </h1>
      <div className="chat-auth-buttons">
        {!user ? (
          <div>
            <button onClick={() => handleNavigator(ROUTERS.SIGNUP)}>
              Đăng ký
            </button>
            <button onClick={() => handleNavigator(ROUTERS.LOGIN)}>
              Đăng nhập
            </button>
          </div>
        ) : (
          <button onClick={handleLogOut}>Đăng xuất</button>
        )}
      </div>
    </header>
  );
};

export default Header;
