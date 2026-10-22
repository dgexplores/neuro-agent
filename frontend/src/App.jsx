import React, { useState } from 'react';
import { Routes, Route, Navigate, Link } from 'react-router-dom';
import { Container, AppBar, Toolbar, Typography, Box, TextField, Button, Alert, Stack } from '@mui/material';
import HomePage from './components/HomePage';
import DiagnosisPage from './components/DiagnosisPage';
import CaseHistoryPage from './components/CaseHistoryPage';
import Navigation from './components/Navigation';
import './App.css';

function App() {
  const [token, setToken] = useState(() => sessionStorage.getItem('neuroagent_token') || '');
  const [message, setMessage] = useState('');
  const saveToken = (event) => {
    event.preventDefault();
    if (!token.trim()) {
      setMessage('Enter a bearer token issued for your backend.');
      return;
    }
    sessionStorage.setItem('neuroagent_token', token.trim());
    setMessage('Session token saved for this tab.');
  };
  const clearToken = () => {
    sessionStorage.removeItem('neuroagent_token');
    setToken('');
    setMessage('Session token cleared.');
  };
  return (
    <div className="App">
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            NeuroAgent — Educational AI Assessment
          </Typography>
        </Toolbar>
      </AppBar>

      <Navigation />

      <Container maxWidth="lg">
        <Box component="form" onSubmit={saveToken} sx={{ mt: 3 }} aria-label="API session token">
          <Typography variant="h6" component="h2">Connect your API session</Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Use a short-lived bearer token issued for your backend. Use synthetic inputs only.
            Tokens stay in this browser tab until cleared. Never enter an AWS key or signing secret.
          </Typography>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <TextField label="Bearer token" type="password" value={token}
              onChange={(event) => setToken(event.target.value)} fullWidth autoComplete="off" />
            <Button type="submit" variant="contained">Save token</Button>
            <Button type="button" onClick={clearToken}>Clear token</Button>
          </Stack>
          {message && <Alert severity="info" sx={{ mt: 2 }} role="status">{message}</Alert>}
        </Box>
        <Box sx={{ my: 4 }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/diagnosis" element={<DiagnosisPage />} />
            <Route path="/history" element={<CaseHistoryPage />} />
            <Route path="/cases" element={<Navigate to="/history" replace />} />
            <Route path="*" element={<Box>
              <Typography variant="h4" component="h1">Page not found</Typography>
              <Typography>The address does not match a page in this application.</Typography>
              <Button component={Link} to="/">Go home</Button>
            </Box>} />
          </Routes>
        </Box>
      </Container>
    </div>
  );
}

export default App;
