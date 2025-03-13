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
