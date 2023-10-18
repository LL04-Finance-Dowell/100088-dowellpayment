import vector from '../assets/illustration.svg'

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

            <div className="section">
              <p className="question">Powered By</p>
              <p className="answer">
              Dowell Living lab.....
              </p>
            </div>
          </div>
          <img src={vector} alt='Vector' className="vector2" />
        </div>
    )
}

export default Details