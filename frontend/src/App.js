import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material';
import HomePage from './components/HomePage';
import DiagnosisPage from './components/DiagnosisPage';
import CaseHistoryPage from './components/CaseHistoryPage';
import Navigation from './components/Navigation';
import './App.css';

function App() {
  return (
    <div className="App">
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            NeuroAgent - AI診療助手
          </Typography>
        </Toolbar>
      </AppBar>

      <Navigation />

      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/diagnosis" element={<DiagnosisPage />} />
            <Route path="/history" element={<CaseHistoryPage />} />
          </Routes>
        </Box>
      </Container>
    </div>
  );
}

export default App;
