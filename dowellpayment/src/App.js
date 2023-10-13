import { useEffect, useState } from "react";


// component
import Modal from "./modal/Modal";
import Form from "./component/Form";

function App() {
  const [isModalOpen, setModalOpen] = useState(false);
  const [state, setState] = useState(null)
  const [loading, setLoading] = useState(false)
  const [info, setInfo] = useState({
    base_currency: "",
    base_price: 0,
    base_country: "",
    target_country: "",
    target_currency: ""
  })

  const [result, setResult] = useState(null)

  useEffect(() => {
    const fetchData = async (url) => {
      const res = await fetch(url)
      const data = await res.json()
      setState(data.data)
    }

    fetchData('https://100088.pythonanywhere.com/api/v1/country-currency')
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
      }

    } catch (error) {
      console.error('Fetch Error:', error);
    }
  }

  const openModal = () => {
    if(info.target_currency !== "" && info.target_country !== "" && info.base_country !== "" && info.base_currency !== "") {
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
      base_price: 0,
      base_country: "",
      target_country: "",
      target_currency: ""
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
        <div className="right-col">
          <img src='/illustration.svg' alt='Vector' className="vector" />
          <div className="faq">
            <div className="section">
              <p className="question">How can we help?</p>
              <p className="answer">
                DoWell World Price indicator is calculating based on Purchasing Power Parity calculation. Use any currency in any country as base then calculate for any country and any currency as target
              </p>
            </div>

            <div className="section">
              <p className="question">How it works?</p>
              <p className="answer">
              Scenario- if I am buying a product for 100 USD in Germany, How much I have to pay for the same product in USA in British Pound?
              </p>
            </div>

            <div className="section">
              <p className="question">Powered By</p>
              <p className="answer">
              DoWell UX Living lab.....
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
