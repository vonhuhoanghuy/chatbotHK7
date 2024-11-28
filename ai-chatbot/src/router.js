import { Route, Routes } from "react-router-dom";

import { ROUTERS } from "./router/path";

import ChatApp from "./pages/user/ChatApp";

import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import MasterLayout from "./pages/theme/MasterLayout";
import LayoutUser from "./pages/user/LayoutUser";

const RouterCustom = () => {
  return (
    <Routes>
      <Route element={<MasterLayout />}>
        <Route path={ROUTERS.HOMEPAGE} element={<LayoutUser />} />
        <Route path={ROUTERS.LOGIN} element={<Login />} />
        <Route path={ROUTERS.SIGNUP} element={<Register />} />
      </Route>
    </Routes>
  );
};

export default RouterCustom;
