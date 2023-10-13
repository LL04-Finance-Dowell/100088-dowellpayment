import React from 'react'
import { Button, Icon, Select, Spinner } from '@chakra-ui/react'
import { MdArrowDropDown } from 'react-icons/md'

const Form = ({ onChange, state, info, handleCalculation, openModal, loading }) => {
    // console.log(state)
    return (
        <>
            <div className="left-col">
                <div className="header">
                    <img src='/dowell-logo.svg' alt='Company logo' className="logo" />
                    <h1 className="title">DoWell World Price Indicator</h1>
                    <p className='desc'>Purchase Price Parity Calculator</p>
                </div>

                <form className="form" onSubmit={handleCalculation}>
                    <div className="form-group">
                    <label>Base Currency</label>
                    <Select 
                        onChange={onChange}
                        name='base_currency'
                        style={{ borderRadius: '60px', height: '60px', textIndent: '10px' }}
                        placeholder="Select Currency"
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
                        {state?.currency_name?.map((currency, key) => (
                            <option key={key} value={currency}>{currency}</option>
                        ))}
                    </Select>
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
                    <Select
                        onChange={onChange}
                        name='base_country'
                        style={{ borderRadius: '60px', height: '60px', textIndent: '10px' }}
                        placeholder="Select Country"
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
                        placeholder="Select Country"
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
                        placeholder="Select Currency"
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
