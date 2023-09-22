import React, { useState, useEffect } from "react";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import { Typography } from "@mui/material";
import axios from "axios";
import MenuItem from "@mui/material/MenuItem";
import {
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableBody,
  TableCell
} from "@mui/material";
import Paper from "@mui/material/Paper";
import Header from "./components/Header";
import "./components/Loader.css";
import PageLoader from "./components/PageLoader";

const DOWELL_PPP_URL = "https://100088.pythonanywhere.com/api/v1/ppp";
const DOWELL_CURRENCY_URL = "https://100088.pythonanywhere.com/api/v1/ppp";

const Home = () => {
  const homeContainerStyle = {
    marginTop: "20px"
  };

  const [inputs, setInputs] = useState({
    base_currency: "",
    base_price: "",
    base_country: "",
    target_country: "",
    target_currency: ""
  });
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [currencies, setCurrencies] = useState([]);

  useEffect(() => {
    axios
      .get(DOWELL_CURRENCY_URL)
      .then((response) => {
        setCurrencies(response.data.data);
      })
      .catch((error) => {
        console.error("Error fetching currencies:", error);
      });
  }, []);

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setInputs((prevInputs) => ({
      ...prevInputs,
      [name]: value
    }));
  };

  const handleApiCall = (e) => {
    e.preventDefault();
    setLoading(true);
    axios
      .post(DOWELL_PPP_URL, inputs)
      .then((response) => {
        setResults(response.data);
        setError("");
        setInputs({
          base_currency: "",
          base_price: "",
          base_country: "",
          target_country: "",
          target_currency: ""
        });
      })
      .catch((error) => {
        setError("An error occurred. Please check your input.");
        setInputs({
          base_currency: "",
          base_price: "",
          base_country: "",
          target_country: "",
          target_currency: ""
        });
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const bodyStyle = {
    maxWidth: "800px",
    width: "90%", 
    margin: "0 auto",
    padding: "24px",
    backgroundColor: "#f9f9f9",
    boxShadow: "0px 2px 4px rgba(0, 0, 0, 0.1)",
    borderRadius: "10px"
  };

  const submitButtonStyle = {
    borderRadius: "5.895px",
    background: "#F4C64D",
    color: "#fff"
  };

  return (
    <>
      <Header />
      {loading && <PageLoader />}
      <div style={{ ...bodyStyle, ...homeContainerStyle }}>
        <TextField
          name="base_currency"
          label="Base Currency"
          select
          value={inputs.base_currency}
          onChange={handleInputChange}
          fullWidth
          variant="outlined"
          margin="normal"
        >
          {currencies.map((currency) => (
            <MenuItem
              key={currency.currency_name}
              value={currency.currency_name}
            >
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
        >
          {currencies.map((currency) => (
            <MenuItem
              key={currency.currency_name}
              value={currency.currency_name}
            >
              {currency.currency_name}
            </MenuItem>
          ))}
        </TextField>
        <Typography variant="body2" color="textSecondary">
          <i>
          * Base currency and base price are reference points for comparing
          exchange rates with the base country, followed by comparing PPP
          calculations with the target country, and converting the target
          currency with exchange rates.
          </i>
        </Typography>

        <br />
        <br />

        <Button
          variant="contained"
          color="primary"
          onClick={handleApiCall}
          style={submitButtonStyle}
        >
          SUBMIT
        </Button>
        {error && (
          <div style={{ color: "red", marginTop: "16px" }}>{error}</div>
        )}
        {results && (
          <>
            <br />
            <br />
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell style={{fontWeight: "bold"}}>Items</TableCell>
                    <TableCell style={{fontWeight: "bold"}}>Value</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell style={{fontWeight: "bold"}}>Base currency exchange rate</TableCell>
                    <TableCell style={{fontWeight: "bold"}}>
                      {results?.base_currency_exchange_rate}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell style={{fontWeight: "bold"}}>Purchasing power</TableCell>
                    <TableCell style={{fontWeight: "bold"}}>{results?.purchasing_power}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell style={{fontWeight: "bold"}}>Target currency exchange rate</TableCell>
                    <TableCell style={{fontWeight: "bold"}}>
                      {results?.target_currency_exchange_rate}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </>
        )}
      </div>
    </>
  );
};

export default Home;
