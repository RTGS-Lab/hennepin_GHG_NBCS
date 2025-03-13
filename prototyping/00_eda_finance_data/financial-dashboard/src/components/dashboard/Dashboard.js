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
