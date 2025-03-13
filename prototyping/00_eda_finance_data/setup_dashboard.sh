#!/bin/bash

# Create React app
echo "Creating React application..."
npx create-react-app financial-dashboard

# Navigate to project directory
cd financial-dashboard

# Install dependencies
echo "Installing dependencies..."
npm install \
  @mui/material @mui/icons-material @emotion/react @emotion/styled \
  recharts \
  react-router-dom \
  papaparse \
  lodash \
  date-fns

# Create project structure
echo "Setting up project structure..."
mkdir -p src/components/charts
mkdir -p src/components/filters
mkdir -p src/components/dashboard
mkdir -p src/components/layout
mkdir -p src/data
mkdir -p src/utils
mkdir -p src/context
mkdir -p public/data

# Copy data file to public folder
echo "Copying data file..."
cp ../clean_financial_data.csv public/data/

# Create core utility files
echo "Creating utility files..."

# Create data loading utility
cat > src/utils/dataLoader.js << 'EOF'
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
EOF

# Create data processing utility
cat > src/utils/dataProcessor.js << 'EOF'
import { groupBy, sumBy, map, sortBy } from 'lodash';
import { format, parse, parseISO } from 'date-fns';

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
          dataByDate[dateKey].expenses += item.Monetary_Amount || 0;
        } else {
          dataByDate[dateKey].revenue += Math.abs(item.Monetary_Amount || 0);
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

# Create context for global data state
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

# Create main layout components
cat > src/components/layout/Header.js << 'EOF'
import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import BarChartIcon from '@mui/icons-material/BarChart';

const Header = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <BarChartIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div">
          Hennepin County Financial Dashboard
        </Typography>
        <Box sx={{ flexGrow: 1 }} />
        <Typography variant="subtitle2">
          Natural Resource Management & Carbon Sequestration
        </Typography>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
EOF

# Create filter components
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
  const transactionTypeOptions = ['All', 'Expense', 'Revenue'];

  return (
    <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Filters
      </Typography>
      
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={3}>
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
        
        <Grid item xs={12} sm={6} md={3}>
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

# Create chart components
cat > src/components/charts/SummaryMetrics.js << 'EOF'
import React from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import ReceiptIcon from '@mui/icons-material/Receipt';
import FolderIcon from '@mui/icons-material/Folder';
import GroupWorkIcon from '@mui/icons-material/GroupWork';
import { useData } from '../../context/DataContext';
import { calculateSummaryMetrics, formatCurrency } from '../../utils/dataProcessor';

const MetricCard = ({ title, value, icon, color }) => {
  return (
    <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
      <Box display="flex" alignItems="center">
        <Box mr={2}>
          {icon}
        </Box>
        <Box>
          <Typography variant="body2" color="text.secondary">
            {title}
          </Typography>
          <Typography variant="h5" component="div">
            {value}
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

const SummaryMetrics = () => {
  const { filteredData, loading } = useData();
  
  if (loading) {
    return <Typography>Loading metrics...</Typography>;
  }
  
  const {
    totalExpenses,
    totalRevenue,
    netAmount,
    uniqueDepartments,
    uniqueProjects,
    recordCount
  } = calculateSummaryMetrics(filteredData);
  
  return (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      <Grid item xs={12} sm={6} md={4}>
        <MetricCard
          title="Total Expenses"
          value={formatCurrency(totalExpenses)}
          icon={<TrendingUpIcon sx={{ color: 'error.main', fontSize: 40 }} />}
          color="error.main"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={4}>
        <MetricCard
          title="Total Revenue"
          value={formatCurrency(totalRevenue)}
          icon={<TrendingDownIcon sx={{ color: 'success.main', fontSize: 40 }} />}
          color="success.main"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={4}>
        <MetricCard
          title="Net Amount"
          value={formatCurrency(netAmount)}
          icon={<ReceiptIcon sx={{ color: 'info.main', fontSize: 40 }} />}
          color="info.main"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={4}>
        <MetricCard
          title="Departments"
          value={uniqueDepartments}
          icon={<GroupWorkIcon sx={{ color: 'warning.main', fontSize: 40 }} />}
          color="warning.main"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={4}>
        <MetricCard
          title="Projects"
          value={uniqueProjects}
          icon={<FolderIcon sx={{ color: 'primary.main', fontSize: 40 }} />}
          color="primary.main"
        />
      </Grid>
      <Grid item xs={12} sm={6} md={4}>
        <MetricCard
          title="Transactions"
          value={recordCount.toLocaleString()}
          icon={<ReceiptIcon sx={{ color: 'secondary.main', fontSize: 40 }} />}
          color="secondary.main"
        />
      </Grid>
    </Grid>
  );
};

export default SummaryMetrics;
EOF

cat > src/components/charts/BarChart.js << 'EOF'
import React from 'react';
import { Paper, Typography, Box } from '@mui/material';
import { BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
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

const BarChart = ({ title, dataKey, valueField = 'Amount_Abs', limit = 10, showLegend = true }) => {
  const { filteredData, loading } = useData();
  
  if (loading) {
    return <Typography>Loading chart...</Typography>;
  }
  
  const chartData = groupDataByField(filteredData, dataKey, valueField, limit);
  
  return (
    <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Box height={350}>
        <ResponsiveContainer width="100%" height="100%">
          <RechartsBarChart
            data={chartData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} angle={-45} textAnchor="end" height={70} />
            <YAxis tickFormatter={(value) => formatCurrency(value)} />
            <Tooltip content={<CustomTooltip />} />
            {showLegend && <Legend />}
            <Bar dataKey="value" name="Amount" fill="#3f51b5" />
          </RechartsBarChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default BarChart;
EOF

cat > src/components/charts/LineChart.js << 'EOF'
import React from 'react';
import { Paper, Typography, Box, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useData } from '../../context/DataContext';
import { groupDataByTimePeriod, formatCurrency } from '../../utils/dataProcessor';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <Paper elevation={3} sx={{ p: 1 }}>
        <Typography variant="body2">{label}</Typography>
        {payload.map((entry, index) => (
          <Typography 
            key={`tooltip-${index}`} 
            variant="body2" 
            style={{ color: entry.color }}
          >
            {`${entry.name}: ${formatCurrency(entry.value)}`}
          </Typography>
        ))}
      </Paper>
    );
  }

  return null;
};

const LineChart = ({ title }) => {
  const { filteredData, loading } = useData();
  const [timePeriod, setTimePeriod] = React.useState('month');
  
  const handlePeriodChange = (event) => {
    setTimePeriod(event.target.value);
  };
  
  if (loading) {
    return <Typography>Loading chart...</Typography>;
  }
  
  const chartData = groupDataByTimePeriod(filteredData, timePeriod);
  
  return (
    <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">
          {title}
        </Typography>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel id="time-period-label">Period</InputLabel>
          <Select
            labelId="time-period-label"
            id="time-period"
            value={timePeriod}
            label="Period"
            onChange={handlePeriodChange}
          >
            <MenuItem value="month">Monthly</MenuItem>
            <MenuItem value="quarter">Quarterly</MenuItem>
            <MenuItem value="year">Yearly</MenuItem>
          </Select>
        </FormControl>
      </Box>
      <Box height={350}>
        <ResponsiveContainer width="100%" height="100%">
          <RechartsLineChart
            data={chartData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="label" />
            <YAxis tickFormatter={(value) => formatCurrency(value)} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line type="monotone" dataKey="expenses" name="Expenses" stroke="#f44336" activeDot={{ r: 8 }} />
            <Line type="monotone" dataKey="revenue" name="Revenue" stroke="#4caf50" />
            <Line type="monotone" dataKey="net" name="Net" stroke="#2196f3" />
          </RechartsLineChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default LineChart;
EOF

cat > src/components/charts/PieChart.js << 'EOF'
import React from 'react';
import { Paper, Typography, Box } from '@mui/material';
import { PieChart as RechartsPieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useData } from '../../context/DataContext';
import { groupDataByField, formatCurrency } from '../../utils/dataProcessor';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#A4DE6C', '#D0ED57', '#FFC658', '#FF5722'];

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <Paper elevation={3} sx={{ p: 1 }}>
        <Typography variant="body2">{payload[0].name}</Typography>
        <Typography variant="body2" color="primary.main">
          {`Amount: ${formatCurrency(payload[0].value)}`}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {`Percentage: ${(payload[0].percent * 100).toFixed(2)}%`}
        </Typography>
      </Paper>
    );
  }

  return null;
};

const PieChart = ({ title, dataKey, valueField = 'Amount_Abs', limit = 10 }) => {
  const { filteredData, loading } = useData();
  
  if (loading) {
    return <Typography>Loading chart...</Typography>;
  }
  
  const chartData = groupDataByField(filteredData, dataKey, valueField, limit);
  
  // Calculate total for percentage
  const total = chartData.reduce((sum, item) => sum + item.value, 0);
  
  return (
    <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Box height={350}>
        <ResponsiveContainer width="100%" height="100%">
          <RechartsPieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend />
          </RechartsPieChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default PieChart;
EOF

# Create dashboard components
cat > src/components/dashboard/Dashboard.js << 'EOF'
import React from 'react';
import { Container, Grid, Typography, CircularProgress, Box, Alert } from '@mui/material';
import { useData } from '../../context/DataContext';
import FilterPanel from '../filters/FilterPanel';
import SummaryMetrics from '../charts/SummaryMetrics';
import BarChart from '../charts/BarChart';
import LineChart from '../charts/LineChart';
import PieChart from '../charts/PieChart';

const Dashboard = () => {
  const { loading, error, filteredData } = useData();

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
          <BarChart
            title="Top 10 Account Categories"
            dataKey="Account_Category"
            valueField="Amount_Abs"
            limit={10}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <PieChart
            title="Transaction Type Distribution"
            dataKey="Transaction_Type"
            valueField="Amount_Abs"
          />
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
EOF

# Update main App.js
cat > src/App.js << 'EOF'
import React from 'react';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { DataProvider } from './context/DataContext';
import Header from './components/layout/Header';
import Dashboard from './components/dashboard/Dashboard';

// Create a custom theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <DataProvider>
        <Header />
        <Dashboard />
      </DataProvider>
    </ThemeProvider>
  );
}

export default App;
EOF

# Update index.js
cat > src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

# Add a README
cat > README.md << 'EOF'
# Hennepin County Financial Dashboard

This React dashboard provides interactive visualization and analysis tools for exploring Hennepin County's financial data related to natural resource management and carbon sequestration efforts.

## Features

- Interactive data filtering by department, project, year, and transaction type
- Summary metrics for expenses, revenue, and net amounts
- Visualizations for departmental spending, project costs, and time-based analysis
- Clean, responsive UI using Material-UI components

## Getting Started

1. Clone the repository
2. Install dependencies: `npm install`
3. Start the development server: `npm start`
4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Data Source

The dashboard uses cleaned financial transaction data from Hennepin County's natural resource management programs. The data includes:

- Fund information
- Department IDs
- Account codes
- Project identifiers
- Monetary amounts
- Date information
- Transaction details

## Technologies Used

- React.js for UI components
- Material-UI for component styling
- Recharts for data visualizations
- PapaParse for CSV parsing
- Lodash for data manipulation
EOF

echo "Setup complete!"
echo "To start the dashboard, run:"
echo "cd financial-dashboard && npm start"

# Make script executable
chmod +x setup_dashboard.sh