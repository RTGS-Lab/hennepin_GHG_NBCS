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
