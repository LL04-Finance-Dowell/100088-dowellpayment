import { useEffect, useState } from "react";


// component
import Modal from "./modal/Modal";
import Form from "./component/Form";
import Details from "./component/Details";

function App() {
  const [isModalOpen, setModalOpen] = useState(false);
  const [state, setState] = useState(null)
  const [loading, setLoading] = useState(false)
  const [info, setInfo] = useState({
    base_currency: "",
    base_price: "",
    base_country: "",
    target_country: "",
    target_currency: "",
    email: ""
  })

  const [result, setResult] = useState(null)

  useEffect(() => {
    const fetchData = async (url) => {
      const res = await fetch(url)
      const data = await res.json()
      setState(data)
    }
console.log(result);
    fetchData('https://100088.pythonanywhere.com/api/v1/ppp')
  }, [])

  const onChange = (e) => {
    const { name, value } = e.target
    setInfo({
      ...info,
      [name]: value
    })
  }

  const handleCalculation = async (e) => {
    e.preventDefault()

    info.target_currency && setLoading(true)

    const requestOption = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(info)
    };
    try {
      const response = await fetch('https://100088.pythonanywhere.com/api/v1/ppp', requestOption)
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const responseData = await response.json();
      setResult(responseData)

      if(responseData.success === true) {
        openModal()
        setLoading(false)
        setInfo({
          ...info,
          base_price: "",
          base_country: "",
          target_country: "",
          target_currency: "",
          email: ""
        })
      }

    } catch (error) {
      console.error('Fetch Error:', error);
      setLoading(false)
    }
  }

  const handleMailing = async () => {
    const reqOption = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(result)
    };

    try {
      const response = await fetch('https://100088.pythonanywhere.com/api/v1/ppp/client-mail', reqOption)
      if(response.ok) {
        alert('Mail sent successfully')
      }
      closeModal()

    } catch (error) {
      console.error('Fetch Error:', error);
    }
  }

  const openModal = () => {
    if(info.target_currency !== "" && info.target_country !== "" && info.base_country !== "" && info.base_currency !== "" && info.email !== "") {
      setTimeout(() => {
        setModalOpen(true);
      }, 1600)
    } else {
      alert("Kindly complete the form")
      setLoading(false)
    }
  };

  const closeModal = () => {
    setLoading(false)
    setModalOpen(false);
    setInfo({
      base_currency: "",
      base_price: "",
      base_country: "",
      target_country: "",
      target_currency: "",
      email: ""
    })
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
        />

        {/* right col */}
        <Details />
      </div>
    </>
  );
}

export default App;
