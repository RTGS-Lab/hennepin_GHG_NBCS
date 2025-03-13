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
