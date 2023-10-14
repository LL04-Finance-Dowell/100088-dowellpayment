import React from 'react'
import { Button, Icon, Spinner, Select } from '@chakra-ui/react'
import { MdArrowDropDown } from 'react-icons/md'
import logo from '../assets/dowell-logo.svg'
// import Select from "react-select"


const Form = ({ onChange, state, info, handleCalculation, openModal, loading }) => {

    return (
        <>
            <div className="left-col">
                <div className="header">
                    <img src={logo} alt='Company logo' className="logo" />
                    <h1 className="title">DoWell World Price Indicator</h1>
                    <p className='desc'>Purchase Price Parity Calculator</p>
                </div>

                <form className="form" onSubmit={handleCalculation}>
                    <div className="form-group">
                    <label>Base Currency</label>
                    {/* <Select 
                        options={state?.currency_name}
                        value={info.base_currency}
                        onChange={onChange}
                        name="base_currency"
                    /> */}
                    <Select 
                        onChange={onChange}
                        name='base_currency'
                        style={{ borderRadius: '60px', height: '60px', textIndent: '10px' }}
                        // placeholder="Select Currency"
                        bg='#FBDDF9'
                        border='none'
                        icon={
                        <Icon
                            as={MdArrowDropDown} 
                            color='#972EA2'
                            boxSize={6}
                            mr={4}
                        />
                        }
                    >
                        <option value="" selected={info.base_currency === ""}>Select Currency</option>
                        {state?.currency_name?.map((currency, key) => (
                            <option key={key} value={currency}>{currency}</option>
                        ))}
                    </Select>
                    </div>
                    <div className="form-group">
                    <label>Base Price</label>
                    <input 
                        type="number" 
                        placeholder="Input Price"
                        name='base_price'
                        value={info?.base_price}
                        onChange={onChange}
                    />
                    </div>
                    <div className="form-group">
                    <label>Base Country</label>
                    <Select
                        onChange={onChange}
                        name='base_country'
                        style={{ borderRadius: '60px', height: '60px', textIndent: '10px' }}
                        // placeholder="Select Country"
                        bg='#FBDDF9'
                        border='none'
                        icon={
                        <Icon
                            as={MdArrowDropDown} 
                            color='#972EA2'
                            boxSize={6}
                            mr={4}
                        />
                        }
                    >
                        <option value="" selected={info.base_country === ""}>Select Country</option>
                        {state?.country_name?.map((country, key) => (
                            <option key={key} value={country}>{country}</option>
                        ))}
                    </Select>
                    </div>
                    <div className="form-group">
                    <label>Target Country</label>
                    <Select
                        onChange={onChange}
                        name='target_country'
                        style={{ borderRadius: '60px', height: '60px', textIndent: '10px' }}
                        // placeholder="Select Country"
                        bg='#FBDDF9'
                        border='none'
                        icon={
                        <Icon
                            as={MdArrowDropDown} 
                            color='#972EA2'
                            boxSize={6}
                            mr={4}
                        />
                        }
                    >
                        <option value="" selected={info.target_country === ""}>Select Country</option>
                        {state?.country_name?.map((country, key) => (
                            <option key={key} value={country}>{country}</option>
                        ))}
                    </Select>
                    </div>
                    <div className="form-group">
                    <label>Target Currency</label>
                    <Select
                        onChange={onChange}
                        name='target_currency'
                        style={{ borderRadius: '60px', height: '60px', textIndent: '10px' }}
                        // placeholder="Select Currency"
                        bg='#FBDDF9'
                        border='none'
                        icon={
                        <Icon
                            as={MdArrowDropDown} 
                            color='#972EA2'
                            boxSize={6}
                            mr={4}
                        />
                        }
                    >
                        <option value="" selected={info.target_currency === ""}>Select Currency</option>
                        {state?.currency_name?.map((currency, key) => (
                            <option key={key} value={currency}>{currency}</option>
                        ))}
                    </Select>
                    </div>
                    <Button 
                    type="submit"
                    onClick={openModal}
                    width='100%'
                    color='white'
                    bg='#972EA2'
                    mt={4}
                    fontSize={{ sm: '1em', md: '1.2em', lg: '1.2em' }}
                    style={{ borderRadius: '60px', height: '60px' }}
                    _hover={{ background: '#ae40ba'}}
                    >
                        {loading ? <Spinner /> : 'Calculate'}
                    </Button>
                </form>
            </div>
        </>
    )
}

export default Form
