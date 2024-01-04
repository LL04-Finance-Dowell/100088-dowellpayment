const SAVED_BASED_CURRENCIES_KEY = 'saved-based-currencies';
const SAVED_BASED_COUNTRIES_KEY = 'saved-based-countries';
const SAVED_TARGET_COUNTRIES_KEY = 'saved-target-countries';
const SAVED_TARGET_CURRENCIES_KEY = 'saved-target-currencies';

export const getUserRecentHistory = () => {
  let savedBaseCurrencies, savedBaseCountries, savedTargetCountries, savedTargetCurrencies;

  try {
    const [
      parsedSavedBaseCurrencies,
      parsedSavedBaseCountries,
      parsedSavedTargetCountries,
      parsedSavedTargetCurrencies,
    ] = [
      JSON.parse(localStorage.getItem(SAVED_BASED_CURRENCIES_KEY)),
      JSON.parse(localStorage.getItem(SAVED_BASED_COUNTRIES_KEY)),
      JSON.parse(localStorage.getItem(SAVED_TARGET_COUNTRIES_KEY)),
      JSON.parse(localStorage.getItem(SAVED_TARGET_CURRENCIES_KEY)),
    ]

    if (!parsedSavedBaseCurrencies) savedBaseCurrencies = [];
    if (!parsedSavedBaseCountries) savedBaseCountries = [];
    if (!parsedSavedTargetCountries) savedTargetCountries = [];
    if (!parsedSavedTargetCurrencies) savedTargetCurrencies = [];

    if (Array.isArray(parsedSavedBaseCurrencies)) savedBaseCurrencies = parsedSavedBaseCurrencies.slice(-5);
    if (Array.isArray(parsedSavedBaseCountries)) savedBaseCountries = parsedSavedBaseCountries.slice(-5);
    if (Array.isArray(parsedSavedTargetCountries)) savedTargetCountries = parsedSavedTargetCountries.slice(-5);
    if (Array.isArray(parsedSavedTargetCurrencies)) savedTargetCurrencies = parsedSavedTargetCurrencies.slice(-5);

  } catch (error) {
    console.log('error parsing recent user history: ', error);

    savedBaseCurrencies = [];
    savedBaseCountries = [];
    savedTargetCountries = [];
    savedTargetCurrencies = [];
  }

  return {
    savedBaseCurrencies,
    savedBaseCountries,
    savedTargetCountries,
    savedTargetCurrencies,
  }
}

export const updateUserRecentHistory = (updatedBaseCurrencies, updatedBaseCountries, updatedTargetCountries, updatedTargetCurrencies) => {
  if (Array.isArray(updatedBaseCountries)) localStorage.setItem(SAVED_BASED_COUNTRIES_KEY, JSON.stringify(updatedBaseCountries))
  if (Array.isArray(updatedBaseCurrencies)) localStorage.setItem(SAVED_BASED_CURRENCIES_KEY, JSON.stringify(updatedBaseCurrencies))
  if (Array.isArray(updatedTargetCountries)) localStorage.setItem(SAVED_TARGET_COUNTRIES_KEY, JSON.stringify(updatedTargetCountries))
  if (Array.isArray(updatedTargetCurrencies)) localStorage.setItem(SAVED_TARGET_CURRENCIES_KEY, JSON.stringify(updatedTargetCurrencies))
} 