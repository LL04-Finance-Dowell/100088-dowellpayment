import React, { useEffect, useState } from 'react'
import { Button, Icon, Spinner } from '@chakra-ui/react'
import { MdArrowDropDown } from 'react-icons/md'
import logo from '../assets/dowell-logo.svg'
import Select from "react-select"
import { getUserRecentHistory } from '../utils'


const Form = ({ onChange, state, info, handleCalculation, openModal, loading }) => {
    // console.log('State: ', state)
    const [ savedDetails, setSavedDetails ] = useState(null);

    const handleClosePage = () => {
        window.close()
    }

    useEffect(() => {
        const { savedBaseCurrencies, savedBaseCountries, savedTargetCountries, savedTargetCurrencies } = getUserRecentHistory();
        
        setSavedDetails({
            savedBaseCurrencies: [...savedBaseCurrencies].reverse(),
            savedBaseCountries: [...savedBaseCountries].reverse(),
            savedTargetCountries: [...savedTargetCountries].reverse(),
            savedTargetCurrencies: [...savedTargetCurrencies].reverse(),
        })
    }, [info])

    return (
        <>
            <div className="left-col">
                <div className="header">
                    <img src={logo} alt='Company logo' className="logo" />
                    <h1 className="title">DoWell World Price Indicator</h1>
                    <p className='desc'>Purchase Power Parity Calculator</p>
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
                        onChange={(val) => onChange({ target: { value: val.value, name: 'base_currency' }})}
                        // name='base_currency'
                        // style={{ borderRadius: '20px', height: '50px', textIndent: '10px' }}
                        // placeholder="Select Currency"
                        // bg='#cccccc84'
                        // border='none'
                        // icon={
                        // <Icon
                        //     as={MdArrowDropDown} 
                        //     color='#972EA2'
                        //     boxSize={6}
                        //     mr={4}
                        // />
                        // }
                        options={
                            !state?.currency || !state ? [
                                // {label: 'Select Currency', value: ''},
                            ]
                            :
                            savedDetails && savedDetails.savedBaseCurrencies ?
                                [...savedDetails.savedBaseCurrencies, ...state?.currency?.filter(item => !savedDetails.savedBaseCurrencies.find(savedItem => savedItem === item))].map((currency => {
                                    return {
                                        label: currency,
                                        value: currency,
                                    }
                                }))
                            :
                            [
                                // {label: 'Select Currency', value: ''},
                                ...state?.currency?.map((currency) => {
                                    return {
                                        label: currency,
                                        value: currency,
                                    }
                                })
                            ]
                        }
                        className='select___'
                        value={{ label: info?.base_currency, value: info?.base_currency }}
                    >
                        {/* <option value="" selected={info.base_currency === ""}>Select Currency</option>
                        {state?.currency?.map((currency, key) => (
                            <option key={key} value={currency}>{currency}</option>
                        ))} */}
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
                        onChange={(val) => onChange({ target: { value: val.value, name: 'base_country' }})}
                        name='base_country'
                        // style={{ borderRadius: '20px', height: '50px', textIndent: '10px' }}
                        // placeholder="Select Country"
                        bg='#cccccc84'
                        border='none'
                        // icon={
                        // <Icon
                        //     as={MdArrowDropDown} 
                        //     color='#972EA2'
                        //     boxSize={6}
                        //     mr={4}
                        // />
                        // }
                        options={
                            !state?.country || !state ? [
                                // {label: 'Select country', value: ''},
                            ]
                            :
                            savedDetails && savedDetails.savedBaseCountries ?
                                [...savedDetails.savedBaseCountries, ...state?.country?.filter(item => !savedDetails.savedBaseCountries.find(savedItem => savedItem === item))].map((country => {
                                    return {
                                        label: country,
                                        value: country,
                                    }
                                }))
                            :
                            [
                                // {label: 'Select country', value: ''},
                                ...state?.country?.map((country) => {
                                    return {
                                        label: country,
                                        value: country,
                                    }
                                })
                            ]    
                        }
                        className='select___'
                        value={{ label: info?.base_country, value: info?.base_country }}
                    >
                        {/* <option value="" selected={info.base_country === ""}>Select Country</option>
                        {state?.country?.map((country, key) => (
                            <option key={key} value={country}>{country}</option>
                        ))} */}
                    </Select>
                    </div>
                    <div className="form-group">
                    <label>Target Country</label>
                    <Select
                        onChange={(val) => onChange({ target: { value: val.value, name: 'target_country' }})}
                        name='target_country'
                        // style={{ borderRadius: '20px', height: '50px', textIndent: '10px' }}
                        // placeholder="Select Country"
                        bg='#cccccc84'
                        border='none'
                        // icon={
                        // <Icon
                        //     as={MdArrowDropDown} 
                        //     color='#972EA2'
                        //     boxSize={6}
                        //     mr={4}
                        // />
                        // }
                        options={
                            !state?.country || !state ? [
                                // {label: 'Select country', value: ''},
                            ]
                            :
                            savedDetails && savedDetails.savedTargetCountries ?
                                [...savedDetails.savedTargetCountries, ...state?.country?.filter(item => !savedDetails.savedTargetCountries.find(savedItem => savedItem === item))].map((country => {
                                    return {
                                        label: country,
                                        value: country,
                                    }
                                }))
                            :
                            [
                                // {label: 'Select country', value: ''},
                                ...state?.country?.map((country) => {
                                    return {
                                        label: country,
                                        value: country,
                                    }
                                })
                            ]
                        }
                        className='select___'
                        value={{ label: info?.target_country, value: info?.target_country }}
                    >
                        {/* <option value="" selected={info.target_country === ""}>Select Country</option>
                        {state?.country?.map((country, key) => (
                            <option key={key} value={country}>{country}</option>
                        ))} */}
                    </Select>
                    </div>
                    <div className="form-group">
                    <label>Target Currency</label>
                    <Select
                        onChange={(val) => onChange({ target: { value: val.value, name: 'target_currency' }})}
                        name='target_currency'
                        // style={{ borderRadius: '20px', height: '50px', textIndent: '10px' }}
                        // placeholder="Select Currency"
                        bg='#cccccc84'
                        border='none'
                        // icon={
                        // <Icon
                        //     as={MdArrowDropDown} 
                        //     color='#972EA2'
                        //     boxSize={6}
                        //     mr={4}
                        // />
                        // }
                        options={
                            !state?.currency || !state ? [
                                // {label: 'Select Currency', value: ''},
                            ]
                            :
                            savedDetails && savedDetails.savedTargetCurrencies ?
                                [...savedDetails.savedTargetCurrencies, ...state?.currency?.filter(item => !savedDetails.savedTargetCurrencies.find(savedItem => savedItem === item))].map((currency => {
                                    return {
                                        label: currency,
                                        value: currency,
                                    }
                                }))
                            :
                            [
                                // {label: 'Select Currency', value: ''},
                                ...state?.currency?.map((currency) => {
                                    return {
                                        label: currency,
                                        value: currency,
                                    }
                                })
                            ]
                        }
                        className='select___'
                        value={{ label: info?.target_currency, value: info?.target_currency }}
                    >
                        {/* <option value="" selected={info.target_currency === ""}>Select Currency</option>
                        {state?.currency?.map((currency, key) => (
                            <option key={key} value={currency}>{currency}</option>
                        ))} */}
                    </Select>
                    </div>
                    <div className="form-group">
                    <label>Your Email Address</label>
                    <input 
                        required
                        type="text" 
                        placeholder="dowell@dowellresearch.uk"
                        name='email'
                        value={info?.email}
                        onChange={onChange}
                        style={{ marginBottom: -10 }}
                    />
                    </div>
                    <div
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            width: '100%',
                            justifyContent: 'space-between',
                            marginTop: '2rem'
                        }}
                    >
                        <Button 
                            type="button"
                            onClick={handleClosePage}
                            width='30%'
                            color='white'
                            bg='#b8b8b8'
                            mt={{ sm: 1, md: 2, lg: 4 }}
                            className='button'
                            fontSize={{ sm: '.8em', md: '1.2em', lg: '1.2em' }}
                            style={{ borderRadius: '20px' }}
                            // h={{ sm: "35px", md: "45px" }}
                            h={45}
                            _hover={{ background: '#808080'}}
                        >
                            {'Close'}
                        </Button>
                        <Button 
                            type="submit"
                            onClick={openModal}
                            width='65%'
                            color='white'
                            bg='#61B84C'
                            mt={{ sm: 1, md: 2, lg: 4 }}
                            className='button'
                            fontSize={{ sm: '.8em', md: '1.2em', lg: '1.2em' }}
                            style={{ borderRadius: '20px' }}
                            // h={{ sm: "35px", md: "45px" }}
                            h={45}
                            _hover={{ background: '#62b84cda'}}
                        >
                            {loading ? <Spinner /> : 'Calculate'}
                        </Button>
                    </div>
                </form>
            </div>
        </>
    )
}

export default Form
