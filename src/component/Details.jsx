import vector from '../assets/images.svg'

const Details = () => {
    return (
        <div className="right-col">
          <img src={vector} alt='Vector' className="vector" />
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

            <div className='section'>
              <p className="question">Disclaimer for Purchase Price Calculator:</p>
              <p className='answer'>
                The Dowell World Price Indicator is used to provide estimates, with data collected solely for this purpose. The purpose-built and trained software offers approximate values, though results may vary with market dynamics. The creators disclaim any liabilities. Data collection complies with GDPR rules. Information obtained is for informational purposes, not professional & legal advice. By acknowledging these terms, Spending based on calculations is at user discretion
              </p>
            </div>
            <div className="section flex">
              <div>
                <p className="question">Powered By</p>
                <p className="answer">DoWell UX Living Lab</p>
              </div>
              <a className= "answer" href="https://visitorbadge.io/status?path=https%3A%2F%2Fll04-finance-dowell.github.io%2F100088-dowellpayment%2F"><img src="https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fll04-finance-dowell.github.io%2F100088-dowellpayment%2F&labelColor=%2337d67a&countColor=%23d9e3f0&labelStyle=upper" alt='dowell link' /></a>
            </div>
          </div>
        </div>
    )
}

export default Details