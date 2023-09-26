import React from "react";
import { Typography } from "@mui/material";

const DescriptionBox = () => {
  const bodyStyle = {
    textAlign: "center",
    padding: "1px",
    marginTop: "2px",
    overflowX: "hidden"
  };
  const containerStyle = {
    maxWidth: "100%"
  };

  return (
    <Typography variant="body2" color="textSecondary">
      <div style={containerStyle}>
        <div style={bodyStyle}>
          <strong>
            Scenario- if I am buying a product for 100 USD in Germany, How much
            I have to pay for the same product in USA in British Pound?
          </strong>
          <br />
          DoWell World Price indicator is calculating based on Purchasing Power
          Parity calculation. Use any currency in any country as base then
          calculate for any country and any currency as target.
        </div>
      </div>
    </Typography>
  );
};

export default DescriptionBox;
