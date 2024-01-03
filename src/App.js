import { useEffect, useState } from "react";

// component
import Modal from "./modal/Modal";
import Form from "./component/Form";
import Details from "./component/Details";
import { toast } from "react-toastify";

function App() {
  const [isModalOpen, setModalOpen] = useState(false);
  const [state, setState] = useState(null);
  console.log(state);
  const [loading, setLoading] = useState(false);
  const [info, setInfo] = useState({
    base_currency: "",
    base_price: "",
    base_country: "",
    target_country: "",
    target_currency: "",
    email: "dowell@dowellresearch.uk",
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

    const requestOption = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ ...info, occurrences }),
    };
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
        openModal();
        setLoading(false);
        // setState({...state,currency:[],country:[]})
        setInfo({
          ...info,
          base_price: "",
          base_country: "",
          target_country: "",
          target_currency: "",
          email: "dowell@dowellresearch.uk",
        });
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
      info.base_currency !== "" &&
      info.email !== ""
    ) {
      setTimeout(() => {
        setModalOpen(true);
      }, 1600);
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
      email: "dowell@dowellresearch.uk",
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
      />
      <div className="container">
        {/* left col */}
        <Form
          onChange={onChange}
          state={state}
          info={info}
          handleCalculation={handleCalculation}
          openModal={openModal}
          loading={loading}
          setLoading={setLoading}
          occurrences={occurrences}
          setOccurrences={setOccurrences}
        />

        {/* right col */}
        <Details />
      </div>
    </>
  );
}

export default App;
