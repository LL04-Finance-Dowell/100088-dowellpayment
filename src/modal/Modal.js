import { Button, Spinner } from "@chakra-ui/react";
import logo from "../assets/dowell-logo.svg";
import { useState } from "react";

function Modal({
  isOpen,
  onClose,
  values,
  info,
  loading,
  handleMailing,
  mailLoading,
  occurrences,
  handleCalculation,
}) {
  const [showData, setShowData] = useState(false);
  const [showCouponInput, setShowCouponInput] = useState(false);
  const [coupon, setCoupon] = useState("");

  const handleContinue = async () => {
    await handleCalculation();
    setShowData(true);
  };

  function toTitleCaseWithSpaces(inputString) {
    return inputString
      .toLowerCase()
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  }

  let basePriceInBaseCountry;
  let basePriceInBaseCountryValue;
  let calculatedPriceInTargetCountry;
  let calculatedPriceInTargetCountryValue;

  for (const key in values) {
    if (key.startsWith("base_price_in_")) {
      basePriceInBaseCountry = toTitleCaseWithSpaces(key);
      basePriceInBaseCountryValue = values[key];
    }
    if (key.startsWith("calculated_price_in")) {
      calculatedPriceInTargetCountry = toTitleCaseWithSpaces(key);
      calculatedPriceInTargetCountryValue = values[key];
    }
  }

  return loading ? (
    <div className="modal-overlay">
      <Spinner />
    </div>
  ) : (
    isOpen && (
      <div className="modal-overlay">
        <div className="modal">
          <button
            className="close-button"
            onClick={() => {
              setShowCouponInput(false);
              setShowData(false);
              onClose();
            }}
          >
            &times;
          </button>
          <div className="header">
            <img src={logo} alt="Company logo" className="modalLogo" />
            <p className="desc">
              <b>Purchase Power Parity Calculator</b>
            </p>
          </div>
          <p>
            Your Experience is :{" "}
            <span style={{ fontSize: 18, fontWeight: 600 }}>{occurrences}</span>
          </p>
          {!showData && (
            <>
              <div
                style={{
                  width: "100%",
                  display: "flex",
                  justifyContent: "space-around",
                  marginTop: 20,
                }}
              >
                <Button
                  onClick={() => {
                    setShowCouponInput(false);
                    setShowData(false);
                    onClose();
                  }}
                  width={"30%"}
                  color="white"
                  bg="#b8b8b8"
                  mt={{ sm: 1, md: 2, lg: 4 }}
                  className="button"
                  fontSize={{ sm: ".8em", md: "1.2em", lg: "1.2em" }}
                  style={{ borderRadius: "20px" }}
                  // h={{ sm: "35px", md: "45px" }}
                  h={45}
                  _hover={{ background: "#808080" }}
                >
                  {loading ? <Spinner /> : "Cancel"}
                </Button>
                {occurrences < 6 && (
                  <Button
                    onClick={handleContinue}
                    width={
                      occurrences === 4 || occurrences === 5 ? "40%" : "65%"
                    }
                    color="white"
                    bg="#61B84C"
                    mt={{ sm: 1, md: 2, lg: 4 }}
                    className="button"
                    fontSize={{ sm: ".8em", md: "1.2em", lg: "1.2em" }}
                    style={{ borderRadius: "20px" }}
                    // h={{ sm: "35px", md: "45px" }}
                    h={45}
                    _hover={{ background: "#62b84cda" }}
                  >
                    {loading ? <Spinner /> : "Continue"}
                  </Button>
                )}
                {(occurrences === 4 ||
                  occurrences === 5 ||
                  occurrences === 6) && (
                  <Button
                    width={
                      occurrences === 4 || occurrences === 5 ? "40%" : "65%"
                    }
                    color="white"
                    bg="#61B84C"
                    mt={{ sm: 1, md: 2, lg: 4 }}
                    className="button"
                    fontSize={{ sm: ".8em", md: "1.2em", lg: "1.2em" }}
                    style={{ borderRadius: "20px" }}
                    // h={{ sm: "35px", md: "45px" }}
                    h={45}
                    _hover={{ background: "#62b84cda" }}
                  >
                    {loading ? <Spinner /> : "Contribute"}
                  </Button>
                )}
              </div>
              {occurrences > 6 && (
                <p style={{ color: "red" }}>
                  Exceeded experienced limits. Please contact our customer
                  support team. Thank you
                </p>
              )}
            </>
          )}
          {!showData &&
            !showCouponInput &&
            (occurrences === 4 || occurrences === 5 || occurrences === 6) && (
              <div className="mailPrompt" style={{ marginTop: 20 }}>
                <p>Do you have a coupon?</p>
                <Button
                  color="white"
                  bg="#61B84C"
                  p={"1 5"}
                  fontSize={"0.875rem"}
                  _hover={{ background: "#62b84cda" }}
                  onClick={() => {
                    setShowCouponInput(true);
                  }}
                >
                  Yes
                </Button>
              </div>
            )}
          {showCouponInput && (
            <div className="mailPrompt" style={{ marginTop: 20 }}>
              <input
                // required
                type="text"
                placeholder="coupon"
                name="coupon"
                value={coupon}
                onChange={(e) => setCoupon(e.target.value)}
                style={{ cursor: "auto", width: "50%" }}
              />
              <Button
                color="white"
                bg="#61B84C"
                p={"1 5"}
                fontSize={"0.875rem"}
                _hover={{ background: "#62b84cda" }}
              >
                Reedem
              </Button>
            </div>
          )}

          {showData && (
            <>
              <div className="info__Price">
                <p className="desc">
                  {basePriceInBaseCountry}: {basePriceInBaseCountryValue}
                </p>
                <p className="desc">
                  {calculatedPriceInTargetCountry}:{" "}
                  {calculatedPriceInTargetCountryValue}
                </p>
              </div>
              <table>
                <tbody
                  style={{
                    border: ".2px solid #cccccc84",
                    borderRadius: "10px",
                  }}
                >
                  <tr className="even">
                    <td style={{ textAlign: "right" }}>Base Currency</td>
                    <td style={{ textAlign: "left" }}>{info?.base_currency}</td>
                  </tr>
                  <tr className="even">
                    <td style={{ textAlign: "right" }}>Base Country</td>
                    <td style={{ textAlign: "left" }}>
                      {values?.base_country}
                    </td>
                  </tr>
                  <tr className="even">
                    <td style={{ textAlign: "right" }}>
                      Price in Base Country
                    </td>
                    <td style={{ textAlign: "left" }}>
                      {values?.price_in_base_country}
                    </td>
                  </tr>
                  <tr className="even">
                    <td style={{ textAlign: "right" }}>Target Country</td>
                    <td style={{ textAlign: "left" }}>
                      {values?.target_country}
                    </td>
                  </tr>
                  <tr className="even">
                    <td style={{ textAlign: "right" }}>
                      Price in target country
                    </td>
                    <td style={{ textAlign: "left" }}>
                      {values?.target_price}
                    </td>
                  </tr>
                  <tr className="even">
                    <td style={{ textAlign: "right" }}>Exchange rate</td>
                    <td style={{ textAlign: "left" }}>
                      1 {values?.base_currency_code} = {values?.exchange_rate}{" "}
                      {values?.target_country_currency_code}
                    </td>
                  </tr>
                </tbody>
              </table>
              <div className="mailPrompt">
                <p>Do you want to mail this?</p>
                <Button
                  color="white"
                  bg="#61B84C"
                  p={"1 5"}
                  fontSize={"0.875rem"}
                  _hover={{ background: "#62b84cda" }}
                  onClick={async () => {
                    await handleMailing();
                    setShowData(false);
                  }}
                  disabled={mailLoading ? true : false}
                >
                  {mailLoading ? "Sending mail..." : "Yes"}
                </Button>
                <Button
                  color="white"
                  bg="#e03131"
                  p={"1 5"}
                  fontSize={"0.875rem"}
                  _hover={{ background: "#f09fa3" }}
                  onClick={() => {
                    setShowCouponInput(false);
                    setShowData(false);
                    onClose();
                  }}
                  disabled={mailLoading ? true : false}
                >
                  {mailLoading ? "Sending mail..." : "No"}
                </Button>
              </div>
            </>
          )}

          {showData && (
            <p className="disclaimer__Wrapp">
              <span className="disclaimer__text">Disclaimer:</span>
              <span className="disclaimer__Info">
                The Dowell World Price Indicator is used to provide estimates,
                with data collected solely for this purpose. The purpose-built
                and trained software offers approximate values, though results
                may vary with market dynamics. The creators disclaim any
                liabilities. Data collection complies with GDPR rules.
                Information obtained is for informational purposes, not
                professional & legal advice. By acknowledging these terms,
                Spending based on calculations is at user discretion
              </span>
            </p>
          )}
        </div>
      </div>
    )
  );
}

export default Modal;
