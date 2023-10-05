import { useEffect, useState } from "react";

function App() {
  const [state, setState] = useState(null)

  useEffect(() => {
    const fetchData = async (url) => {
      const res = fetch(url)
      const data = await res.json()
    }
  }, [])

  return (
    <div className="container">
      {/* left col */}
      <div className="left-col">
        <div>
          <img src='/dowell-logo.svg' alt='Company logo' className="logo" />
          <h1 className="title">DoWell World Price Indicator</h1>
          <p className='desc'>Purchase Price Parity Calculator</p>
        </div>

        <form className="form">
          <div className="form-group">
            <label>Base Currency</label>
            <select>
              <option>Test</option>
              <option>Test2</option>
            </select>
          </div>
          <div className="form-group">
            <label>Base Price</label>
            <input type="number" />
          </div>
          <div className="form-group">
            <label>Base Country</label>
            <select>
              
            </select>
          </div>
          <div className="form-group">
            <label>Target Country</label>
            <select>
              
            </select>
          </div>
          <div className="form-group">
            <label>Target Currency</label>
            <select>
              
            </select>
          </div>
          <button>
            Calculate
          </button>
        </form>
      </div>

      {/* right col */}
      <div className="right-col">
        <img src='/illustration.svg' alt='Company logo' className="logo" />
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
