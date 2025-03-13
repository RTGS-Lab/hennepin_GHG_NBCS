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
