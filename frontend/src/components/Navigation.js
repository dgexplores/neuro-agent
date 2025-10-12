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
    return 0;
  };

  const handleChange = (event, newValue) => {
    const routes = ['/', '/diagnosis', '/history'];
    navigate(routes[newValue]);
  };

  return (
    <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
      <Tabs value={getCurrentTab()} onChange={handleChange} centered>
        <Tab label="首頁" />
        <Tab label="診斷分析" />
        <Tab label="病例記錄" />
      </Tabs>
    </Box>
  );
};

export default Navigation;
