function Modal({ isOpen, onClose, children }) {
    const keys = ['Base Currency', 'Base Price in Base Country', 'Calculated Price in Target Base Country', 'Price in Base Country', 'Target Country', 'Target Country Exchange Rate', 'Calculated Price based on Purchasing Power']

    return (
        isOpen && (
        <div className="modal-overlay">
            <div className="modal">
            <button className="close-button" onClick={onClose}>
                &times;
            </button>
            <div>
                <img src='/dowell-logo.svg' alt='Company logo' className="logo" />
                <p className='desc'>Purchase Price Parity Calculator</p>
            </div>
            <table>
                <thead>
                    <tr>
                        <th id='head-left'>Items</th>
                        <th id='head-right'>Values</th>
                    </tr>
                </thead>
                <tbody>
                    {keys?.map((key, i) => (
                        <tr key={i}  className={`${i % 2 === 0 ? 'even' : 'odd'} ${i === keys.length - 1 ? 'last-row' : ''}`}>
                            <td>{key}</td>
                            <td>Values</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            </div>
        </div>
        )
    );
}

export default Modal;
