import { Outlet } from "react-router-dom";
import Header from "../header";
import { UserProvider } from "../../../middleware/UserContext";
import { UserContext } from "../../../middleware/UserContext";
import { useContext } from "react";
const MasterLayout = () => {
  return (
    <UserProvider>
      <div>
        <Header />
        <Outlet />
      </div>
    </UserProvider>
  );
};

export default MasterLayout;
