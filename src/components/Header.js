import React from "react";
import Typography from "@mui/material/Typography";
import logo from "../logo.svg";

const Header = () => {
  const headerStyle = {
    backgroundColor: "#00573412",
    width: "100%",
    height: "60px",
    flexShrink: 0,
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    padding: "0 20px"
  };

  const logoStyle = {
    display: "flex",
    alignItems: "center",
    gap: "10px"
  };

  const headerTextStyle = {
    color: "#005734",
    fontFamily: "Inter",
    fontSize: "26.75px",
    fontStyle: "normal",
    fontWeight: 600,
    lineHeight: "normal"
  };

  return (
    <div style={headerStyle}>
      <div style={logoStyle}>
        <img src={logo} alt="Logo" style={{ height: "40px" }} />
        <Typography variant="h6" style={headerTextStyle}>
          Dowell PPP
        </Typography>
      </div>
    </div>
  );
};

export default Header;
