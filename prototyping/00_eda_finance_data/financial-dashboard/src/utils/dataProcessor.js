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
