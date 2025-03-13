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
