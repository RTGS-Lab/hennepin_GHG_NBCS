#!/bin/bash

# Navigate to the financial dashboard directory
cd financial-dashboard

# Create an account category chart component
cat > src/components/charts/AccountCategoryChart.js << 'EOF'
import React from 'react';
import { Paper, Typography, Box } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useData } from '../../context/DataContext';
import { groupDataByField, formatCurrency } from '../../utils/dataProcessor';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <Paper elevation={3} sx={{ p: 1 }}>
        <Typography variant="body2">{label}</Typography>
        <Typography variant="body2" color="primary.main">
          {`Amount: ${formatCurrency(payload[0].value)}`}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {`Count: ${payload[0].payload.count} transactions`}
        </Typography>
      </Paper>
    );
  }

  return null;
};

const AccountCategoryChart = () => {
  const { filteredData, loading } = useData();
  
  if (loading) {
    return <Typography>Loading chart...</Typography>;
  }
  
  // Group data by Account_Category
  const chartData = groupDataByField(filteredData, 'Account_Category', 'Amount_Abs', 10);
  
  return (
    <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Top 10 Account Categories by Amount
      </Typography>
      <Box height={350}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} angle={-45} textAnchor="end" height={70} />
            <YAxis tickFormatter={(value) => formatCurrency(value)} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar dataKey="value" name="Amount" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default AccountCategoryChart;
EOF

# Create a journal entries table component
cat > src/components/dashboard/JournalEntriesTable.js << 'EOF'
import React, { useState } from 'react';
import { 
  Paper, Typography, Box, Table, TableBody, TableCell, 
  TableContainer, TableHead, TableRow, TablePagination,
  TextField, InputAdornment, IconButton, Chip
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import { useData } from '../../context/DataContext';
import { formatCurrency } from '../../utils/dataProcessor';

const JournalEntriesTable = () => {
  const { filteredData, loading } = useData();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Handle pagination
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  // Handle search
  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
    setPage(0);
  };
  
  const clearSearch = () => {
    setSearchTerm('');
    setPage(0);
  };
  
  if (loading) {
    return <Typography>Loading journal entries...</Typography>;
  }
  
  // Filter data based on search term
  const filteredEntries = searchTerm
    ? filteredData.filter(entry => 
        Object.values(entry).some(value => 
          String(value).toLowerCase().includes(searchTerm.toLowerCase())
        )
      )
    : filteredData;
  
  // Sort by date descending and paginate
  const sortedEntries = [...filteredEntries].sort((a, b) => 
    new Date(b['Journal Date']) - new Date(a['Journal Date'])
  );
  
  const displayEntries = sortedEntries.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );
  
  return (
    <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Journal Entries
      </Typography>
      
      <Box mb={2}>
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          placeholder="Search journal entries..."
          value={searchTerm}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
            endAdornment: searchTerm && (
              <InputAdornment position="end">
                <IconButton size="small" onClick={clearSearch}>
                  <ClearIcon />
                </IconButton>
              </InputAdornment>
            )
          }}
        />
      </Box>
      
      <TableContainer sx={{ maxHeight: 400 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Department</TableCell>
              <TableCell>Account</TableCell>
              <TableCell>Project</TableCell>
              <TableCell>Description</TableCell>
              <TableCell align="right">Amount</TableCell>
              <TableCell>Type</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {displayEntries.map((entry, index) => (
              <TableRow key={index} hover>
                <TableCell>
                  {new Date(entry['Journal Date']).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  {entry['Department_Name']}
                </TableCell>
                <TableCell>
                  {entry['Account']}
                </TableCell>
                <TableCell>
                  {entry['Project_Name']}
                </TableCell>
                <TableCell>
                  {entry['Line Description']}
                </TableCell>
                <TableCell align="right">
                  {formatCurrency(entry['Monetary Amount'])}
                </TableCell>
                <TableCell>
                  <Chip 
                    label={entry['Transaction_Type']} 
                    color={entry['Transaction_Type'] === 'Expense' ? 'error' : 'success'} 
                    size="small"
                    variant="outlined" 
                  />
                </TableCell>
              </TableRow>
            ))}
            {displayEntries.length === 0 && (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No journal entries match your criteria
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      <TablePagination
        component="div"
        count={filteredEntries.length}
        page={page}
        onPageChange={handleChangePage}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        rowsPerPageOptions={[10, 25, 50, 100]}
      />
    </Paper>
  );
};

export default JournalEntriesTable;
EOF

# Update the filter panel to include account category filter
cat > src/components/filters/FilterPanel.js << 'EOF'
import React from 'react';
import { Paper, Typography, Grid, FormControl, InputLabel, Select, MenuItem, TextField, Button, Box } from '@mui/material';
import { useData } from '../../context/DataContext';

const FilterPanel = () => {
  const { filters, updateFilters, resetFilters, getFilterOptions } = useData();

  const handleChange = (e) => {
    const { name, value } = e.target;
    updateFilters({ [name]: value });
  };

  const departmentOptions = getFilterOptions('Department_Name');
  const projectOptions = getFilterOptions('Project_Name');
  const yearOptions = getFilterOptions('Year');
  const accountCategoryOptions = getFilterOptions('Account_Category');
  const transactionTypeOptions = ['All', 'Expense', 'Revenue'];

  return (
    <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Filters
      </Typography>
      
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel id="department-label">Department</InputLabel>
            <Select
              labelId="department-label"
              id="department"
              name="department"
              value={filters.department}
              label="Department"
              onChange={handleChange}
            >
              {departmentOptions.map(option => (
                <MenuItem key={option} value={option}>{option}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel id="project-label">Project</InputLabel>
            <Select
              labelId="project-label"
              id="project"
              name="project"
              value={filters.project}
              label="Project"
              onChange={handleChange}
            >
              {projectOptions.map(option => (
                <MenuItem key={option} value={option}>{option}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel id="account-category-label">Account Category</InputLabel>
            <Select
              labelId="account-category-label"
              id="accountCategory"
              name="accountCategory"
              value={filters.accountCategory}
              label="Account Category"
              onChange={handleChange}
            >
              {accountCategoryOptions.map(option => (
                <MenuItem key={option} value={option}>{option}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel id="year-label">Year</InputLabel>
            <Select
              labelId="year-label"
              id="year"
              name="year"
              value={filters.year}
              label="Year"
              onChange={handleChange}
            >
              {yearOptions.map(option => (
                <MenuItem key={option} value={option}>{option}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel id="transaction-type-label">Transaction Type</InputLabel>
            <Select
              labelId="transaction-type-label"
              id="transactionType"
              name="transactionType"
              value={filters.transactionType}
              label="Transaction Type"
              onChange={handleChange}
            >
              {transactionTypeOptions.map(option => (
                <MenuItem key={option} value={option}>{option}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} sm={6} md={2}>
          <Box display="flex" justifyContent="flex-end" height="100%">
            <Button 
              variant="outlined" 
              onClick={resetFilters}
              sx={{ height: '40px' }}
            >
              Reset Filters
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default FilterPanel;
EOF

# Update the DataContext to include account category filter
cat > src/context/DataContext.js << 'EOF'
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
EOF

# Update the data processor utility to include account category filter
cat > src/utils/dataProcessor.js << 'EOF'
import { groupBy, sumBy, map, sortBy } from 'lodash';
import { format, parseISO } from 'date-fns';

// Format currency values
export const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

// Calculate summary metrics for dashboard
export const calculateSummaryMetrics = (data) => {
  const totalExpenses = sumBy(
    data.filter(item => item.Transaction_Type === 'Expense'), 
    'Monetary Amount'
  );
  
  const totalRevenue = Math.abs(sumBy(
    data.filter(item => item.Transaction_Type === 'Revenue'), 
    'Monetary Amount'
  ));
  
  const netAmount = sumBy(data, 'Monetary Amount');
  
  const uniqueDepartments = new Set(data.map(item => item.Department_Name)).size;
  const uniqueProjects = new Set(data.map(item => item.Project_Name)).size;
  
  return {
    totalExpenses,
    totalRevenue,
    netAmount,
    uniqueDepartments,
    uniqueProjects,
    recordCount: data.length,
  };
};

// Group data by a specific field for visualizations
export const groupDataByField = (data, field, valueField = 'Amount_Abs', limit = 10) => {
  const grouped = groupBy(data, field);
  
  let result = map(grouped, (items, key) => ({
    name: key,
    value: sumBy(items, valueField),
    count: items.length
  }));
  
  // Sort by value descending and limit results
  result = sortBy(result, item => -item.value);
  
  if (limit > 0) {
    result = result.slice(0, limit);
  }
  
  return result;
};

// Group data by time period for time series
export const groupDataByTimePeriod = (data, period = 'month') => {
  // Create a date key based on the period
  const getDateKey = (item) => {
    const date = parseISO(item['Journal Date']);
    
    switch (period) {
      case 'day':
        return format(date, 'yyyy-MM-dd');
      case 'month':
        return format(date, 'yyyy-MM');
      case 'quarter':
        return `${format(date, 'yyyy')}-Q${Math.ceil(date.getMonth() + 1) / 3}`;
      case 'year':
        return format(date, 'yyyy');
      default:
        return format(date, 'yyyy-MM');
    }
  };
  
  // Create a formatted label for display
  const getDateLabel = (dateKey) => {
    if (period === 'month') {
      const [year, month] = dateKey.split('-');
      return format(new Date(parseInt(year), parseInt(month) - 1, 1), 'MMM yyyy');
    }
    return dateKey;
  };
  
  try {
    // Group data by the date key
    const dataByDate = {};
    
    data.forEach(item => {
      try {
        const dateKey = getDateKey(item);
        if (!dataByDate[dateKey]) {
          dataByDate[dateKey] = {
            expenses: 0,
            revenue: 0
          };
        }
        
        if (item.Transaction_Type === 'Expense') {
          dataByDate[dateKey].expenses += Number(item.Monetary_Amount) || 0;
        } else {
          dataByDate[dateKey].revenue += Math.abs(Number(item.Monetary_Amount) || 0);
        }
      } catch (e) {
        console.error('Error processing item:', item, e);
      }
    });
    
    // Convert to array for chart
    const result = Object.keys(dataByDate).map(dateKey => ({
      date: dateKey,
      label: getDateLabel(dateKey),
      expenses: dataByDate[dateKey].expenses,
      revenue: dataByDate[dateKey].revenue,
      net: dataByDate[dateKey].expenses - dataByDate[dateKey].revenue
    }));
    
    // Sort by date
    return sortBy(result, 'date');
  } catch (e) {
    console.error('Error in groupDataByTimePeriod:', e);
    return [];
  }
};

// Filter data based on various criteria
export const filterData = (data, filters) => {
  return data.filter(item => {
    // Apply department filter
    if (filters.department && filters.department !== 'All' && 
        item.Department_Name !== filters.department) {
      return false;
    }
    
    // Apply project filter
    if (filters.project && filters.project !== 'All' && 
        item.Project_Name !== filters.project) {
      return false;
    }
    
    // Apply account category filter
    if (filters.accountCategory && filters.accountCategory !== 'All' && 
        item.Account_Category !== filters.accountCategory) {
      return false;
    }
    
    // Apply year filter
    if (filters.year && filters.year !== 'All' && 
        item.Year !== parseInt(filters.year)) {
      return false;
    }
    
    // Apply transaction type filter
    if (filters.transactionType && filters.transactionType !== 'All' && 
        item.Transaction_Type !== filters.transactionType) {
      return false;
    }
    
    // Apply amount range filter
    if (filters.minAmount && item.Amount_Abs < filters.minAmount) {
      return false;
    }
    
    if (filters.maxAmount && item.Amount_Abs > filters.maxAmount) {
      return false;
    }
    
    return true;
  });
};
EOF

# Update the main Dashboard component to include the new components
cat > src/components/dashboard/Dashboard.js << 'EOF'
import React, { useState } from 'react';
import { Container, Grid, Typography, CircularProgress, Box, Alert, Tabs, Tab } from '@mui/material';
import { useData } from '../../context/DataContext';
import FilterPanel from '../filters/FilterPanel';
import SummaryMetrics from '../charts/SummaryMetrics';
import BarChart from '../charts/BarChart';
import LineChart from '../charts/LineChart';
import PieChart from '../charts/PieChart';
import AccountCategoryChart from '../charts/AccountCategoryChart';
import JournalEntriesTable from './JournalEntriesTable';

const Dashboard = () => {
  const { loading, error, filteredData } = useData();
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading financial data...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (filteredData.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <FilterPanel />
        <Alert severity="info">
          No data matches the selected filters. Try adjusting your filters.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <FilterPanel />
      
      <SummaryMetrics />
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Charts & Graphs" />
          <Tab label="Journal Entries" />
        </Tabs>
      </Box>
      
      {tabValue === 0 ? (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <LineChart title="Expenses & Revenue Over Time" />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <BarChart
              title="Top 10 Projects by Amount"
              dataKey="Project_Name"
              valueField="Amount_Abs"
              limit={10}
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <PieChart
              title="Expenditure by Department"
              dataKey="Department_Name"
              valueField="Amount_Abs"
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <AccountCategoryChart />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <PieChart
              title="Transaction Type Distribution"
              dataKey="Transaction_Type"
              valueField="Amount_Abs"
            />
          </Grid>
        </Grid>
      ) : (
        <JournalEntriesTable />
      )}
    </Container>
  );
};

export default Dashboard;
EOF

echo "Dashboard update script has been created."
echo "To apply these updates, navigate to the financial-dashboard directory and run:"
echo "1. cd financial-dashboard"
echo "2. npm start"

# Make script executable
chmod +x update_dashboard.sh