import React from "react";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import MenuItem from "@mui/material/MenuItem";

const FormComponent = ({
  inputs,
  currencies,
  handleInputChange,
  handleApiCall
}) => {
  const formContainerStyle = {
    border: "1px solid #ccc",
    borderRadius: "5px",
    padding: "20px",
    marginRight: "50px",
    width: "500px"
  };
  const textFieldStyle = {
    width: "100%"
  };

  return (
    <div style={formContainerStyle}>
      <TextField
        name="base_currency"
        label="Base Currency"
        select
        value={inputs.base_currency}
        onChange={handleInputChange}
        fullWidth
        variant="outlined"
        margin="normal"
        style={textFieldStyle}
      >
        {currencies.map((currency) => (
          <MenuItem key={currency.currency_name} value={currency.currency_name}>
            {currency.currency_name}
          </MenuItem>
        ))}
      </TextField>
      <TextField
        name="base_price"
        label="Base Price"
        value={inputs.base_price}
        onChange={handleInputChange}
        fullWidth
        variant="outlined"
        margin="normal"
        style={textFieldStyle}
      />
      <TextField
        name="base_country"
        label="Base Country"
        select
        value={inputs.base_country}
        onChange={handleInputChange}
        fullWidth
        variant="outlined"
        margin="normal"
        style={textFieldStyle}
      >
        {currencies.map((country) => (
          <MenuItem key={country.country_name} value={country.country_name}>
            {country.country_name}
          </MenuItem>
        ))}
      </TextField>
      <TextField
        name="target_country"
        label="Target Country"
        select
        value={inputs.target_country}
        onChange={handleInputChange}
        fullWidth
        variant="outlined"
        margin="normal"
        style={textFieldStyle}
      >
        {currencies.map((country) => (
          <MenuItem key={country.country_name} value={country.country_name}>
            {country.country_name}
          </MenuItem>
        ))}
      </TextField>
      <TextField
        name="target_currency"
        label="Target Currency"
        select
        value={inputs.target_currency}
        onChange={handleInputChange}
        fullWidth
        variant="outlined"
        margin="normal"
        style={textFieldStyle}
      >
        {currencies.map((currency) => (
          <MenuItem key={currency.currency_name} value={currency.currency_name}>
            {currency.currency_name}
          </MenuItem>
        ))}
      </TextField>
      <Button
        variant="contained"
        color="primary"
        onClick={handleApiCall}
        style={{
          borderRadius: "5.895px",
          background: "#F4C64D",
          color: "#fff"
        }}
      >
        SUBMIT
      </Button>
    </div>
  );
};

export default FormComponent;
