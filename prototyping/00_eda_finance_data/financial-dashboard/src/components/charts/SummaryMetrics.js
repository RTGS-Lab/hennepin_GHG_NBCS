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
