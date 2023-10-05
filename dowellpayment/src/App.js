
function App() {
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

            </select>
          </div>
          <div className="form-group">
            <label>Base Price</label>
            <select>
              
            </select>
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
        <h1>Dowell Payment</h1>
      </div>
    </div>
  );
}

export default App;
