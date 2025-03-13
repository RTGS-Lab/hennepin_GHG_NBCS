import React, { useState } from 'react';
import { 
  Paper, Typography, Box, Table, TableBody, TableCell, 
  TableContainer, TableHead, TableRow, TablePagination,
  TextField, InputAdornment, IconButton, Chip
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import { useData } from '../../context/DataContext';
import { formatCurrency } from '../../utils/dataProcessor';

const JournalEntriesTable = () => {
  const { filteredData, loading } = useData();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Handle pagination
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  // Handle search
  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
    setPage(0);
  };
  
  const clearSearch = () => {
    setSearchTerm('');
    setPage(0);
  };
  
  if (loading) {
    return <Typography>Loading journal entries...</Typography>;
  }
  
  // Filter data based on search term
  const filteredEntries = searchTerm
    ? filteredData.filter(entry => 
        Object.values(entry).some(value => 
          String(value).toLowerCase().includes(searchTerm.toLowerCase())
        )
      )
    : filteredData;
  
  // Sort by date descending and paginate
  const sortedEntries = [...filteredEntries].sort((a, b) => 
    new Date(b['Journal Date']) - new Date(a['Journal Date'])
  );
  
  const displayEntries = sortedEntries.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );
  
  return (
    <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Journal Entries
      </Typography>
      
      <Box mb={2}>
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          placeholder="Search journal entries..."
          value={searchTerm}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
            endAdornment: searchTerm && (
              <InputAdornment position="end">
                <IconButton size="small" onClick={clearSearch}>
                  <ClearIcon />
                </IconButton>
              </InputAdornment>
            )
          }}
        />
      </Box>
      
      <TableContainer sx={{ maxHeight: 400 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Department</TableCell>
              <TableCell>Account</TableCell>
              <TableCell>Project</TableCell>
              <TableCell>Description</TableCell>
              <TableCell align="right">Amount</TableCell>
              <TableCell>Type</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {displayEntries.map((entry, index) => (
              <TableRow key={index} hover>
                <TableCell>
                  {new Date(entry['Journal Date']).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  {entry['Department_Name']}
                </TableCell>
                <TableCell>
                  {entry['Account']}
                </TableCell>
                <TableCell>
                  {entry['Project_Name']}
                </TableCell>
                <TableCell>
                  {entry['Line Description']}
                </TableCell>
                <TableCell align="right">
                  {formatCurrency(entry['Monetary Amount'])}
                </TableCell>
                <TableCell>
                  <Chip 
                    label={entry['Transaction_Type']} 
                    color={entry['Transaction_Type'] === 'Expense' ? 'error' : 'success'} 
                    size="small"
                    variant="outlined" 
                  />
                </TableCell>
              </TableRow>
            ))}
            {displayEntries.length === 0 && (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No journal entries match your criteria
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      <TablePagination
        component="div"
        count={filteredEntries.length}
        page={page}
        onPageChange={handleChangePage}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        rowsPerPageOptions={[10, 25, 50, 100]}
      />
    </Paper>
  );
};

export default JournalEntriesTable;
