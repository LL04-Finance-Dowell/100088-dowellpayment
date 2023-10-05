import { useEffect, useState } from "react";

function App() {
  const [state, setState] = useState(null)
  const [info, setInfo] = useState({
    base_currency: "",
    base_price: 0,
    base_country: "",
    target_country: "",
    target_currency: ""
  })

  useEffect(() => {
    const fetchData = async (url) => {
      const res = await fetch(url)
      const data = await res.json()
      setState(data.data)
    }

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

      // const responseData = await response.json();
      // console.log('Response Data:', responseData);
      setInfo({
        base_currency: "",
        base_price: 0,
        base_country: "",
        target_country: "",
        target_currency: ""
      })

    } catch (error) {
      console.error('Fetch Error:', error);
    }
  }


  return (
    <div className="container">
      {/* left col */}
      <div className="left-col">
        <div>
          <img src='/dowell-logo.svg' alt='Company logo' className="logo" />
          <h1 className="title">DoWell World Price Indicator</h1>
          <p className='desc'>Purchase Price Parity Calculator</p>
        </div>

        <form className="form" onSubmit={handleCalculation}>
          <div className="form-group">
            <label>Base Currency</label>
            <select 
              onChange={onChange}
              name='base_currency'
            >
              <option>{"Select Currency"}</option>
              {state?.map((currency, key) => (
                <option key={key} value={currency?.currency_name}>{currency?.currency_name}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Base Price</label>
            <input 
              type="number" 
              placeholder="($) Input Price"
              name='base_price'
              value={info?.base_price}
              onChange={onChange}
            />
          </div>
          <div className="form-group">
            <label>Base Country</label>
            <select
              onChange={onChange}
              name='base_country'
            >
              <option>{"Select Country"}</option>
              {state?.map((country, key) => (
                <option key={key} value={country?.country_name}>{country?.country_name}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Target Country</label>
            <select
              onChange={onChange}
              name='target_country'
            >
              <option>{"Select Country"}</option>
              {state?.map((country, key) => (
                <option key={key} value={country?.country_name}>{country?.country_name}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Target Currency</label>
            <select
              onChange={onChange}
              name='target_currency'
            >
              <option>{"Select Currency"}</option>
              {state?.map((currency, key) => (
                <option key={key} value={currency?.currency_name}>{currency?.currency_name}</option>
              ))}
            </select>
          </div>
          <button>
            Calculate
          </button>
        </form>
      </div>

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
            Dowell Living lab.....
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
