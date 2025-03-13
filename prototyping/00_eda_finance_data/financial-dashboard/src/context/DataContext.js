import React, { createContext, useState, useEffect, useContext } from 'react';
import { loadFinancialData } from '../utils/dataLoader';
import { filterData } from '../utils/dataProcessor';

// Create context
const DataContext = createContext();

// Create provider component
export const DataProvider = ({ children }) => {
  const [rawData, setRawData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    department: 'All',
    project: 'All',
    accountCategory: 'All',
    year: 'All',
    transactionType: 'All',
    minAmount: null,
    maxAmount: null
  });

  // Load data on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await loadFinancialData();
        setRawData(data);
        setFilteredData(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load financial data');
        setLoading(false);
        console.error('Error loading data:', err);
      }
    };

    fetchData();
  }, []);

  // Apply filters when they change
  useEffect(() => {
    if (rawData.length > 0) {
      const filtered = filterData(rawData, filters);
      setFilteredData(filtered);
    }
  }, [filters, rawData]);

  // Get unique values for filter options
  const getFilterOptions = (field) => {
    if (!rawData.length) return [];
    
    const options = Array.from(new Set(rawData.map(item => item[field])))
      .filter(Boolean)
      .sort();
      
    return ['All', ...options];
  };

  // Update filters
  const updateFilters = (newFilters) => {
    setFilters(prevFilters => ({
      ...prevFilters,
      ...newFilters
    }));
  };

  // Reset filters
  const resetFilters = () => {
    setFilters({
      department: 'All',
      project: 'All',
      accountCategory: 'All',
      year: 'All',
      transactionType: 'All',
      minAmount: null,
      maxAmount: null
    });
  };

  // Context value
  const value = {
    rawData,
    filteredData,
    loading,
    error,
    filters,
    updateFilters,
    resetFilters,
    getFilterOptions
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
};

// Custom hook for using the data context
export const useData = () => {
  const context = useContext(DataContext);
  if (context === undefined) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
};
