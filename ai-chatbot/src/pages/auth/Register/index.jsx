import React, { useState } from "react";
import axios from "axios";
import "./style.scss";
import { ROUTERS } from "../../../router/path";
import { useNavigate } from "react-router-dom";

const Register = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigator = useNavigate();
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://127.0.0.1:5000/api/register", {
        username,
        password
      });
      if (response.data.message === "Đăng ký thành công") {
        alert("Đăng ký thành công!");
        setUsername("");
        setPassword("");
      }
      navigator(ROUTERS.LOGIN);
    } catch (err) {
      setError("Đã xảy ra lỗi! Vui lòng thử lại.");
    }
  };

  return (
    <div className="register-form">
      <h2>Đăng Ký</h2>
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
        <button type="submit">Đăng Ký</button>
      </form>
    </div>
  );
};

export default Register;
