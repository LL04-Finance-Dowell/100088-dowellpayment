import { useEffect, useState } from "react";

// component
import Modal from "./modal/Modal";
import Form from "./component/Form";
import Details from "./component/Details";
import { toast } from "react-toastify";
import { getUserRecentHistory, updateUserRecentHistory } from "./utils";

function App() {
  const [isModalOpen, setModalOpen] = useState(false);
  const [state, setState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [info, setInfo] = useState({
    base_currency: "",
    base_price: "",
    base_country: "",
    target_country: "",
    target_currency: "",
    email: "",
  });
  const [result, setResult] = useState(null);
  const [mailLoading, setMailLoading] = useState(false);
  const [occurrences, setOccurrences] = useState(null);

  useEffect(() => {
    const fetchData = async (url) => {
      const res = await fetch(url);
      const data = await res.json();
      setState(data);
    };

    fetchData("https://100088.pythonanywhere.com/api/v1/ppp");
  }, []);

  const onChange = (e) => {
    const { name, value } = e.target;
    setInfo({
      ...info,
      [name]: value,
    });
  };

  const handleCalculation = async () => {
    info.target_currency && setLoading(true);

    if (info.email.length < 1) info.email = "dowell@dowellresearch.uk";

    const requestOption = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ ...info, occurrences }),
    };

    const {
      savedBaseCurrencies,
      savedBaseCountries,
      savedTargetCountries,
      savedTargetCurrencies,
    } = getUserRecentHistory();
    const copyOfInfo = { ...info };

    try {
      const response = await fetch(
        "https://100088.pythonanywhere.com/api/v1/ppp",
        requestOption
      );
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const responseData = await response.json();
      setResult(responseData);

      if (responseData.success === true) {
        setLoading(false);
        setInfo({
          ...info,
          base_price: "",
          base_country: "",
          target_country: "",
          target_currency: "",
          email: "",
        });

        if (savedBaseCurrencies.includes(copyOfInfo.base_currency)) {
          const foundPreviousItemIndex = savedBaseCurrencies.indexOf(
            copyOfInfo.base_currency
          );
          if (foundPreviousItemIndex > -1)
            savedBaseCurrencies.splice(foundPreviousItemIndex, 1);
        }

        if (savedBaseCountries.includes(copyOfInfo.base_country)) {
          const foundPreviousItemIndex = savedBaseCountries.indexOf(
            copyOfInfo.base_country
          );
          if (foundPreviousItemIndex > -1)
            savedBaseCountries.splice(foundPreviousItemIndex, 1);
        }

        if (savedTargetCountries.includes(copyOfInfo.target_country)) {
          const foundPreviousItemIndex = savedTargetCountries.indexOf(
            copyOfInfo.target_country
          );
          if (foundPreviousItemIndex > -1)
            savedTargetCountries.splice(foundPreviousItemIndex, 1);
        }

        if (savedTargetCurrencies.includes(copyOfInfo.target_currency)) {
          const foundPreviousItemIndex = savedTargetCurrencies.indexOf(
            copyOfInfo.target_currency
          );
          if (foundPreviousItemIndex > -1)
            savedTargetCurrencies.splice(foundPreviousItemIndex, 1);
        }

        savedBaseCurrencies.push(copyOfInfo.base_currency);
        savedBaseCountries.push(copyOfInfo.base_country);
        savedTargetCountries.push(copyOfInfo.target_country);
        savedTargetCurrencies.push(copyOfInfo.target_currency);

        updateUserRecentHistory(
          savedBaseCurrencies,
          savedBaseCountries,
          savedTargetCountries,
          savedTargetCurrencies
        );
      }
    } catch (error) {
      console.error("Fetch Error:", error);
      setLoading(false);
    }
  };

  const handleMailing = async () => {
    if (mailLoading) return;

    setMailLoading(true);

    const reqOption = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(result),
    };

    try {
      const response = await fetch(
        "https://100088.pythonanywhere.com/api/v1/ppp/client-mail",
        reqOption
      );
      setMailLoading(false);
      if (response.ok) {
        toast.success("Mail sent successfully");
      }
      closeModal();
    } catch (error) {
      console.error("Fetch Error:", error);
      setMailLoading(false);
    }
  };

  const openModal = () => {
    if (
      info.target_currency !== "" &&
      info.target_country !== "" &&
      info.base_country !== "" &&
      info.base_currency !== ""
      // &&
      // info.email !== ""
    ) {
      setModalOpen(true);
    } else {
      toast.info("Kindly complete the form");
      setLoading(false);
    }
  };

  const closeModal = () => {
    setLoading(false);
    setModalOpen(false);
    setInfo({
      base_currency: "",
      base_price: "",
      base_country: "",
      target_country: "",
      target_currency: "",
      email: "",
    });
  };

  return (
    <>
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        values={result}
        info={info}
        loading={loading}
        handleMailing={handleMailing}
        mailLoading={mailLoading}
        occurrences={occurrences}
        handleCalculation={handleCalculation}
      />
      <div className="container">
        {/* left col */}
        <Form
          onChange={onChange}
          state={state}
          info={info}
          openModal={openModal}
          loading={loading}
          setLoading={setLoading}
          setOccurrences={setOccurrences}
        />

        {/* right col */}
        <Details />
      </div>
    </>
  );
}

export default App;
