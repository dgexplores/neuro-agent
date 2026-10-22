import React from 'react';
import { Box, Tabs, Tab } from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';

const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const getCurrentTab = () => {
    if (location.pathname === '/') return 0;
    if (location.pathname === '/diagnosis') return 1;
    if (location.pathname === '/history') return 2;
    return false;
  };

  const handleChange = (event, newValue) => {
    const routes = ['/', '/diagnosis', '/history'];
    navigate(routes[newValue]);
  };

  return (
    <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
      <Tabs value={getCurrentTab()} onChange={handleChange} centered>
        <Tab label="Home" />
        <Tab label="Assessment" />
        <Tab label="Saved cases" />
      </Tabs>
    </Box>
  );
};

export default Navigation;
