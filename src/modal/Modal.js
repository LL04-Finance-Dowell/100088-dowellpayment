import { Button, Spinner } from "@chakra-ui/react";
import logo from "../assets/dowell-logo.svg";

function Modal({
  isOpen,
  onClose,
  values,
  info,
  loading,
  handleMailing,
  mailLoading,
}) {
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
          <button className="close-button" onClick={onClose}>
            &times;
          </button>
          <div className="header">
            <img src={logo} alt="Company logo" className="modalLogo" />
            <p className="desc">
              <b>Purchase Power Parity Calculator</b>
            </p>
          </div>

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
            {/* <thead>
                    <tr>
                        <th id='head-left'>Items</th>
                        <th id='head-right'>Values</th>
                    </tr>
                </thead> */}
            <tbody
              style={{ border: ".2px solid #cccccc84", borderRadius: "10px" }}
            >
              {/* <tr className="odd">
                        <td id='head-left' style={{ fontWeight: 700 }}>{basePriceInBaseCountry}</td>
                        <td id='head-right' style={{ fontWeight: 700 }}>{basePriceInBaseCountryValue}</td>
                    </tr>
                    <tr className="odd">
                        <td style={{ fontWeight: 700 }}>{calculatedPriceInTargetCountry}</td>
                        <td style={{ fontWeight: 700 }}>{calculatedPriceInTargetCountryValue}</td>
                    </tr> */}
              {/* <tr className="separation"></tr> */}
              <tr className="even">
                <td style={{ textAlign: "right" }}>Base Currency</td>
                <td style={{ textAlign: "left" }}>{info?.base_currency}</td>
              </tr>
              <tr className="even">
                <td style={{ textAlign: "right" }}>Base Country</td>
                <td style={{ textAlign: "left" }}>{values?.base_country}</td>
              </tr>
              <tr className="even">
                <td style={{ textAlign: "right" }}>Price in Base Country</td>
                <td style={{ textAlign: "left" }}>
                  {values?.price_in_base_country}
                </td>
              </tr>
              <tr className="even">
                <td style={{ textAlign: "right" }}>Target Country</td>
                <td style={{ textAlign: "left" }}>{values?.target_country}</td>
              </tr>
              <tr className="even">
                <td style={{ textAlign: "right" }}>Price in target country</td>
                <td style={{ textAlign: "left" }}>{values?.target_price}</td>
              </tr>
              <tr className="even">
                <td style={{ textAlign: "right" }}>Exchange rate</td>
                <td style={{ textAlign: "left" }}>
                  1 {values?.base_currency_code} = {values?.exchange_rate}{" "}
                  {values?.target_country_currency_code}
                </td>
              </tr>
              {/* <tr className="even" style={{ borderRadius: '0 0 10px 10px'}}>
                        <td style={{ borderRadius: '0 0 0 10px'}}>Calculated price in targeted country based on purchasing power</td>
                        <td style={{ borderRadius: '0 0 10px 0'}}>{values?.calculated_price_base_on_ppp}</td>
                    </tr> */}
              {/* <tr className="even">
                        <td>Exchange rate between {values?.base_currency} and {values?.target_currency}</td>
                        <td>{values?.exchange_rate}</td>
                    </tr> */}
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
              onClick={handleMailing}
              disabled={mailLoading ? true : false}
            >
              {mailLoading ? "Sending mail..." : "Yes"}
            </Button>
            <Button
              color="white"
              bg="#61B84C"
              p={"1 5"}
              fontSize={"0.875rem"}
              _hover={{ background: "#62b84cda" }}
              onClick={onClose}
              disabled={mailLoading ? true : false}
            >
              {mailLoading ? "Sending mail..." : "No"}
            </Button>
            {/* <Button
                    color="#972EA2"
                    bg="#FBEFFA"
                    p={1}
                    _hover={{ background: '#FBDDF9'}}
                >
                    No
                </Button> */}
          </div>

          <p className="disclaimer__Wrapp">
            <span className="disclaimer__text">
              Disclaimer for Purchase Power Calculator:
            </span>
            <span className="disclaimer__Info">
              The Dowell World Price Indicator is used to provide estimates,
              with data collected solely for this purpose. The purpose-built and
              trained software offers approximate values, though results may
              vary with market dynamics. The creators disclaim any liabilities.
              Data collection complies with GDPR rules. Information obtained is
              for informational purposes, not professional & legal advice. By
              acknowledging these terms, Spending based on calculations is at
              user discretion
            </span>
          </p>
        </div>
      </div>
    )
  );
}

export default Modal;
