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
