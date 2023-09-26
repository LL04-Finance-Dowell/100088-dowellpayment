import React from "react";

const Footer = () => {
  const FooterStyle = {
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

  const badgeStyle = {
    display: "flex",
    alignItems: "center",
    color: "#263759",
    textDecoration: "none",
    fontWeight: "bold"
  };

  return (
    <div style={FooterStyle}>
      <a
        href="https://visitorbadge.io/status?path=https%3A%2F%2Fll04-finance-dowell.github.io%2F100088-dowellpayment%2F"
        style={badgeStyle}
      >
        <img
          src="https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fll04-finance-dowell.github.io%2F100088-dowellpayment%2F&countColor=%23263759&style=flat&labelStyle=lower"
          alt="Visitor Badge"
          style={{ marginRight: "8px" }}
        />
        Site Visitors
      </a>
    </div>
  );
};

export default Footer;
