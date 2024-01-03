import React, { useState } from "react";
import { Button, Spinner } from "@chakra-ui/react";
import logo from "../assets/dowell-logo.svg";
import Select from "react-select";

const Form = ({
  onChange,
  state,
  info,
  handleCalculation,
  loading,
  setLoading,
  occurrences,
  setOccurrences,
}) => {
  // console.log('State: ', state)
  const [canCalculate, setCanCalculate] = useState(false);
  const handleClosePage = () => {
    window.close();
  };
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (canCalculate) {
      handleCalculation();
      setCanCalculate(false);
    } else {
      try {
        setLoading(true);
        const response = await fetch(
          `https://100105.pythonanywhere.com/api/v3/experience_database_services/?type=get_user_email&product_number=UXLIVINGLAB002&email=${info.email}`
        );
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }

        const responseData = await response.json();
        setOccurrences(responseData.occurrences);
        if (responseData.occurrences !== 0) {
          setCanCalculate(true);
        } else {
          const requestOption = {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              product_number: "UXLIVINGLAB002",
              email: info.email,
            }),
          };
          const response = await fetch(
            `https://100105.pythonanywhere.com/api/v3/experience_database_services/?type=register_user`,
            requestOption
          );
          if (response.ok) {
            setCanCalculate(true);
          } else {
            throw new Error("Network response was not ok");
          }
        }
      } catch (error) {
        console.error("Fetch Error:", error);
      }
      setLoading(false);
    }
  };

  return (
    <>
      <div className="left-col">
        <div className="header">
          <img src={logo} alt="Company logo" className="logo" />
          <h1 className="title">DoWell World Price Indicator</h1>
          <p className="desc">Purchase Power Parity Calculator</p>
        </div>

        <form className="form" onSubmit={handleSubmit} method="post">
          <div className="form-group">
            <label>Base Currency</label>
            {/* <Select 
                        options={state?.currency_name}
                        value={info.base_currency}
                        onChange={onChange}
                        name="base_currency"
                    /> */}
            <Select
              onChange={(val) =>
                onChange({
                  target: { value: val.value, name: "base_currency" },
                })
              }
              // name='base_currency'
              // style={{ borderRadius: '20px', height: '50px', textIndent: '10px' }}
              // placeholder="Select Currency"
              // bg='#cccccc84'
              // border='none'
              // icon={
              // <Icon
              //     as={MdArrowDropDown}
              //     color='#972EA2'
              //     boxSize={6}
              //     mr={4}
              // />
              // }
              options={
                !state?.currency || !state
                  ? [
                      // {label: 'Select Currency', value: ''},
                    ]
                  : [
                      // {label: 'Select Currency', value: ''},
                      ...state?.currency?.map((currency) => {
                        return {
                          label: currency,
                          value: currency,
                        };
                      }),
                    ]
              }
              className="select___"
              value={{ label: info?.base_currency, value: info?.base_currency }}
            >
              {/* <option value="" selected={info.base_currency === ""}>Select Currency</option>
                        {state?.currency?.map((currency, key) => (
                            <option key={key} value={currency}>{currency}</option>
                        ))} */}
            </Select>
          </div>
          <div className="form-group">
            <label>Base Price</label>
            <input
              type="number"
              placeholder="Input Price"
              name="base_price"
              value={info?.base_price}
              onChange={onChange}
            />
          </div>
          <div className="form-group">
            <label>Base Country</label>
            <Select
              onChange={(val) =>
                onChange({ target: { value: val.value, name: "base_country" } })
              }
              name="base_country"
              // style={{ borderRadius: '20px', height: '50px', textIndent: '10px' }}
              // placeholder="Select Country"
              bg="#cccccc84"
              border="none"
              // icon={
              // <Icon
              //     as={MdArrowDropDown}
              //     color='#972EA2'
              //     boxSize={6}
              //     mr={4}
              // />
              // }
              options={
                !state?.country || !state
                  ? [
                      // {label: 'Select country', value: ''},
                    ]
                  : [
                      // {label: 'Select country', value: ''},
                      ...state?.country?.map((country) => {
                        return {
                          label: country,
                          value: country,
                        };
                      }),
                    ]
              }
              className="select___"
              value={{ label: info?.base_country, value: info?.base_country }}
            >
              {/* <option value="" selected={info.base_country === ""}>Select Country</option>
                        {state?.country?.map((country, key) => (
                            <option key={key} value={country}>{country}</option>
                        ))} */}
            </Select>
          </div>
          <div className="form-group">
            <label>Target Country</label>
            <Select
              onChange={(val) =>
                onChange({
                  target: { value: val.value, name: "target_country" },
                })
              }
              name="target_country"
              // style={{ borderRadius: '20px', height: '50px', textIndent: '10px' }}
              // placeholder="Select Country"
              bg="#cccccc84"
              border="none"
              // icon={
              // <Icon
              //     as={MdArrowDropDown}
              //     color='#972EA2'
              //     boxSize={6}
              //     mr={4}
              // />
              // }
              options={
                !state?.country || !state
                  ? [
                      // {label: 'Select country', value: ''},
                    ]
                  : [
                      // {label: 'Select country', value: ''},
                      ...state?.country?.map((country) => {
                        return {
                          label: country,
                          value: country,
                        };
                      }),
                    ]
              }
              className="select___"
              value={{
                label: info?.target_country,
                value: info?.target_country,
              }}
            >
              {/* <option value="" selected={info.target_country === ""}>Select Country</option>
                        {state?.country?.map((country, key) => (
                            <option key={key} value={country}>{country}</option>
                        ))} */}
            </Select>
          </div>
          <div className="form-group">
            <label>Target Currency</label>
            <Select
              onChange={(val) =>
                onChange({
                  target: { value: val.value, name: "target_currency" },
                })
              }
              name="target_currency"
              // style={{ borderRadius: '20px', height: '50px', textIndent: '10px' }}
              // placeholder="Select Currency"
              bg="#cccccc84"
              border="none"
              // icon={
              // <Icon
              //     as={MdArrowDropDown}
              //     color='#972EA2'
              //     boxSize={6}
              //     mr={4}
              // />
              // }
              options={
                !state?.currency || !state
                  ? [
                      // {label: 'Select Currency', value: ''},
                    ]
                  : [
                      // {label: 'Select Currency', value: ''},
                      ...state?.currency?.map((currency) => {
                        return {
                          label: currency,
                          value: currency,
                        };
                      }),
                    ]
              }
              className="select___"
              value={{
                label: info?.target_currency,
                value: info?.target_currency,
              }}
            >
              {/* <option value="" selected={info.target_currency === ""}>Select Currency</option>
                        {state?.currency?.map((currency, key) => (
                            <option key={key} value={currency}>{currency}</option>
                        ))} */}
            </Select>
          </div>
          <div className="form-group">
            <label>Your Email Address</label>
            <input
              required
              type="text"
              placeholder="admin@example.com"
              name="email"
              value={info?.email}
              onChange={onChange}
              style={{ cursor: "auto" }}
            />
          </div>
          {occurrences !== null && (
            <p style={{ fontSize: 17 }}>
              Your Experince is :{" "}
              <span style={{ fontWeight: "500" }}>{occurrences}</span>
            </p>
          )}

          <div
            style={{
              display: "flex",
              alignItems: "center",
              width: "100%",
              justifyContent: "space-between",
              marginTop: "2rem",
            }}
          >
            <Button
              type="button"
              onClick={handleClosePage}
              width="30%"
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
              {"Close"}
            </Button>
            {occurrences !== 6 && (
              <Button
                type="submit"
                width={occurrences === 4 || occurrences === 5 ? "30%" : "65%"}
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
                {loading ? (
                  <Spinner />
                ) : canCalculate ? (
                  "Calculate"
                ) : (
                  "Experience"
                )}
              </Button>
            )}

            {occurrences === 4 || occurrences === 5 || occurrences === 6 ? (
              <Button
                type="submit"
                width={occurrences === 6 ? "65%" : "30%"}
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
            ) : (
              ""
            )}
          </div>
        </form>
      </div>
    </>
  );
};

export default Form;
