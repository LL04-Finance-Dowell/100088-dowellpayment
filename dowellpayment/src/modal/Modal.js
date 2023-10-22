import { Spinner } from "@chakra-ui/react";
import logo from '../assets/dowell-logo.svg'

function Modal({ isOpen, onClose, values, info, loading }) {

    function toTitleCaseWithSpaces(inputString) {
        return inputString
          .toLowerCase()
          .split('_')
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');
      }

    let basePriceInBaseCountry
    let basePriceInBaseCountryValue;
    let calculatedPriceInTargetCountry;
    let calculatedPriceInTargetCountryValue

    for(const key in values) {
        if(key.startsWith("base_price_in_")) {
            basePriceInBaseCountry = toTitleCaseWithSpaces(key)
            basePriceInBaseCountryValue = values[key]
        }
        if(key.startsWith("calculated_price_in")) {
            calculatedPriceInTargetCountry = toTitleCaseWithSpaces(key)
            calculatedPriceInTargetCountryValue = values[key]
        }
    }

    return (
        loading ? 
        <div className="modal-overlay">
            <Spinner /> 
        </div> :
        isOpen && (
        <div className="modal-overlay">
            <div className="modal">
            <button className="close-button" onClick={onClose}>
                &times;
            </button>
            <div className="header">
                <img src={logo} alt='Company logo' className="modalLogo" />
                <p className='desc'>Purchase Price Parity Calculator</p>
            </div>
            <table>
                {/* <thead>
                    <tr>
                        <th id='head-left'>Items</th>
                        <th id='head-right'>Values</th>
                    </tr>
                </thead> */}
                <tbody>
                    <tr className="odd">
                        <td style={{ fontWeight: 700 }}>{basePriceInBaseCountry}</td>
                        <td style={{ fontWeight: 700 }}>{basePriceInBaseCountryValue}</td>
                    </tr>
                    <tr className="even">
                        <td style={{ fontWeight: 700 }}>{calculatedPriceInTargetCountry}</td>
                        <td style={{ fontWeight: 700 }}>{calculatedPriceInTargetCountryValue}</td>
                    </tr>
                    <tr className="even">
                        <td>Base Currency</td>
                        <td>{info?.base_currency}</td>
                    </tr>
                    <tr className="odd">
                        <td>Price in Base Country</td>
                        <td>{values?.price_in_base_country}</td>
                    </tr>
                    <tr className="even">
                        <td>Target Country</td>
                        <td>{values?.target_country}</td>
                    </tr>
                    <tr className="odd">
                        <td>Target Country Exchange Rate</td>
                        <td>{values?.target_price}</td>
                    </tr>
                    <tr className="even" style={{ borderRadius: '0 0 60px 60px'}}>
                        <td style={{ borderRadius: '0 0 0 60px'}}>Calculated Price based on Purchasing Power</td>
                        <td style={{ borderRadius: '0 0 60px 0'}}>{values?.calculated_price_base_on_ppp}</td>
                    </tr>
                </tbody>
            </table>
            </div>
        </div>
        )
    );
}

export default Modal;
