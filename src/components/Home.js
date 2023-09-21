import React, { useState, useEffect } from "react";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import axios from "axios";
import CircularProgress from "@mui/material/CircularProgress";
import MenuItem from "@mui/material/MenuItem";

import {
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableBody,
  TableCell,
} from "@mui/material";
import Paper from "@mui/material/Paper";
import { DOWELL_PPP_URL, DOWELL_CURRENCY_NAME } from "../api.config";

const Home = () => {
  const [inputs, setInputs] = useState({
    base_currency: "",
    base_price: "",
    base_country: "",
    target_country: "",
    target_currency: "",
  });
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [currencies, setCurrencies] = useState([]);

  useEffect(() => {
    axios
      .get(DOWELL_CURRENCY_NAME)
      .then((response) => {
        setCurrencies(response.data.data);
        console.log(response.data.data);
      })
      .catch((error) => {
        console.error("Error fetching currencies:", error);
      });
  }, []);

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setInputs((prevInputs) => ({
      ...prevInputs,
      [name]: value,
    }));
  };

  const handleApiCall = (e) => {
    e.preventDefault();
    setLoading(true);
    axios
      .post(DOWELL_PPP_URL, inputs)
      .then((response) => {
        console.log(response.data);
        setResults(response.data);
        setError("");
        setInputs({
          base_currency: "",
          base_price: "",
          base_country: "",
          target_country: "",
          target_currency: "",
        });
      })
      .catch((error) => {
        setError("An error occurred. Please check your input.");
        setInputs({
          base_currency: "",
          base_price: "",
          base_country: "",
          target_country: "",
          target_currency: "",
        });
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <div
      style={{
        position: "relative",
        backgroundColor: "#f9f9f9",
        borderRadius: "8px",
        boxShadow: "0px 2px 4px rgba(0, 0, 0, 0.1)",
        padding: "24px",
        maxWidth: "600px",
        margin: "0 auto",
        textAlign: "center",
      }}
    >
      <Typography
        variant="h5"
        style={{
          marginBottom: "24px",
          fontWeight: "bold",
          textAlign: "center",
        }}
      >
        DOWELL PPP
      </Typography>
      <small>
        Base currency and base price are reference points for comparing exchange
        rates with the base country, followed by comparing PPP calculations with
        the target country, and converting the target currency with exchange
        rates.
      </small>
      <TextField
        name="base_currency"
        label="base_currency"
        select
        value={inputs.base_currency}
        onChange={handleInputChange}
        fullWidth
        margin="normal"
      >
        {currencies.map((currency) => (
          <MenuItem key={currency.currency_name} value={currency.currency_name}>
            {currency.currency_name}
          </MenuItem>
        ))}
      </TextField>
      <TextField
        name="base_price"
        label="base_price"
        value={inputs.base_price}
        onChange={handleInputChange}
        fullWidth
        margin="normal"
      />
      <TextField
        name="base_country"
        label="base_country"
        select
        value={inputs.base_country}
        onChange={handleInputChange}
        fullWidth
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
        label="target_country"
        select
        value={inputs.target_country}
        onChange={handleInputChange}
        fullWidth
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
        label="target_currency"
        select
        value={inputs.target_currency}
        onChange={handleInputChange}
        fullWidth
        margin="normal"
      >
        {currencies.map((currency) => (
          <MenuItem key={currency.currency_name} value={currency.currency_name}>
            {currency.currency_name}
          </MenuItem>
        ))}
      </TextField>
      <Button variant="contained" color="primary" onClick={handleApiCall}>
        SUBMIT
      </Button>
      {error && <div style={{ color: "red", marginTop: "16px" }}>{error}</div>}
      {loading && <CircularProgress style={{ marginTop: "16px" }} />}{" "}
      {results && (
        <>
          <br />
          <br />

          <TableContainer component={Paper} variant="outlined">
            <Table className="results__Table">
              <TableHead>
                <TableRow>
                  <TableCell>Item</TableCell>
                  <TableCell>Value</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>Base currency exchange rate</TableCell>
                  <TableCell>{results?.base_currency_exchange_rate}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Purchasing power</TableCell>
                  <TableCell>{results?.purchasing_power}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Target currency exchange rate</TableCell>
                  <TableCell>
                    {results?.target_currency_exchange_rate}
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </>
      )}
    </div>
  );
};

export default Home;
