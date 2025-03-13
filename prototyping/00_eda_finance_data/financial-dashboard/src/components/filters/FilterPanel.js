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
