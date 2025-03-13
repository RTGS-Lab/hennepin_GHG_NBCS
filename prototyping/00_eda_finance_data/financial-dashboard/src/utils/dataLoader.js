import Papa from 'papaparse';

export const loadFinancialData = async () => {
  try {
    const response = await fetch('/data/clean_financial_data.csv');
    const csvText = await response.text();
    
    return new Promise((resolve) => {
      Papa.parse(csvText, {
        header: true,
        skipEmptyLines: true,
        dynamicTyping: true,
        complete: (results) => {
          resolve(results.data);
        }
      });
    });
  } catch (error) {
    console.error('Error loading financial data:', error);
    return [];
  }
};
