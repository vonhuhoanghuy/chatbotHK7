import React, { useContext, useState } from "react";
import axios from "axios";
import "./style.scss";
import { ROUTERS } from "../../../router/path";
import { useNavigate } from "react-router-dom";
import { UserContext } from "../../../middleware/UserContext";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { updateUser } = useContext(UserContext);
  const navigator = useNavigate();
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://127.0.0.1:5000/api/login", {
        username,
        password
      });
      if (!response.status == 200) {
        throw new Error(response.statusText);
      }
      const user = response.data.user;

      localStorage.setItem("user", JSON.stringify(user));
      updateUser(user);
      navigator(ROUTERS.HOMEPAGE);
    } catch (err) {
      setError("Tên đăng nhập hoặc mật khẩu không chính xác.");
    }
  };

  return (
    <div className="login-form">
      <h2>Đăng Nhập</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Tên đăng nhập</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Mật khẩu</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <p className="error-message">{error}</p>}
        <button type="submit">Đăng Nhập</button>
      </form>
    </div>
  );
};

export default Login;
