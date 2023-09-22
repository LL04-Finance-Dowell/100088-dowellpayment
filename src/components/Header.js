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
    flexDirection: "column",
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
  const headerTextsStyle = {
    color: "#005734",
    fontFamily: "Inter",
    fontSize: "10.75px",
    fontStyle: "normal",
    fontWeight: 600,
    lineHeight: "normal"
  };

  return (
    <div style={headerStyle}>
      <div style={logoStyle}>
        <img src={logo} alt="Logo" style={{ height: "40px" }} />
        <Typography variant="h6" style={headerTextStyle}>
          DoWell World Price Indicator
        </Typography>
        <br />
      </div>
        <Typography variant="h6" style={headerTextsStyle}>
        Purchase Price Parity Calculator
        </Typography>
    </div>
  );
};

export default Header;
