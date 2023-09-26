import React from "react";
import Typography from "@mui/material/Typography";
import logo from "../logo.svg";
import {
  headerStyle,
  headerTextStyle,
  headerTextsStyle,
  logoStyle
} from "../styles";

const Header = () => {
  return (
    <div style={headerStyle}>
      <div style={logoStyle}>
        <img src={logo} alt="Logo" style={{ height: "40px" }} />
        <Typography variant="h6" style={headerTextStyle}>
          DoWell World Price Indicator
        </Typography>
      </div>
      <Typography variant="h6" style={headerTextsStyle}>
        Purchase Price Parity Calculator
      </Typography>
    </div>
  );
};

export default Header;
