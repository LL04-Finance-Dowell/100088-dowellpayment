import React, { useState, useEffect } from "react";
import axios from "axios";
import FormComponent from "./Form";
import ResultComponent from "./Results";
import DescriptionBox from "./Description";
import PageLoader from "./Loader";
import Footer from "./Footer";
import { bodyStyle, formStyle, resultsStyle } from "../styles";

// const DOWELL_PPP_URL = "https://100088.pythonanywhere.com/api/v1/ppp";
const DOWELL_PPP_URL = "http://127.0.0.1:8000/api/v1/ppp";

const HomePage = () => {
  const homeContainerStyle = {
    marginTop: "20px",
    display: "flex",
    justifyContent: "center",
  };

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
      .get(DOWELL_PPP_URL)
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
      [name]: value,
    }));
  };

  const handleApiCall = (e) => {
    e.preventDefault();
    setLoading(true);
    axios
      .post(DOWELL_PPP_URL, inputs)
      .then((response) => {
        setResults(response.data);
        console.log(response.data);
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
    <>
      <DescriptionBox />
      {loading && <PageLoader />}
      <div style={homeContainerStyle}>
        <div style={bodyStyle}>
          <FormComponent
            inputs={inputs}
            currencies={currencies}
            handleInputChange={handleInputChange}
            handleApiCall={handleApiCall}
            style={formStyle}
          />
          <ResultComponent
            results={results}
            error={error}
            style={resultsStyle}
          />
        </div>
      </div>
      <Footer />
    </>
  );
};

export default HomePage;
