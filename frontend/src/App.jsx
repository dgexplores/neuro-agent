import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import { Container, AppBar, Toolbar, Typography, Box, TextField, Button, Alert, Stack } from '@mui/material';
import HomePage from './components/HomePage';
import DiagnosisPage from './components/DiagnosisPage';
import CaseHistoryPage from './components/CaseHistoryPage';
import Navigation from './components/Navigation';
import DemoAssessmentPage from './components/DemoAssessmentPage';
import { getDemoConfig, startDemoSession } from './services/api';
import './App.css';

function App() {
  const navigate = useNavigate();
  const [token, setToken] = useState(() => sessionStorage.getItem('neuroagent_token') || '');
  const [message, setMessage] = useState('');
  const [advanced, setAdvanced] = useState(false);
  const [demoConfig, setDemoConfig] = useState(null);
  const [startingDemo, setStartingDemo] = useState(false);
  const [demoSession, setDemoSession] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem('neuroagent_demo_session') || 'null'); }
    catch { return null; }
  });
  useEffect(() => {
    let mounted = true;
    getDemoConfig().then((config) => { if (mounted) setDemoConfig(config); }).catch(() => {});
    return () => { mounted = false; };
  }, []);
  useEffect(() => {
    if (!demoSession) return undefined;
    const expire = () => {
      sessionStorage.removeItem('neuroagent_token');
      sessionStorage.removeItem('neuroagent_demo_session');
      setToken('');
      setDemoSession(null);
      setMessage('Your demo session expired. Start a new synthetic demo to continue.');
    };
    const remaining = demoSession.expiresAt - Date.now();
    if (remaining <= 0) { expire(); return undefined; }
    const timeout = setTimeout(expire, remaining);
    return () => clearTimeout(timeout);
  }, [demoSession]);
  const startDemo = async () => {
    if (startingDemo) return;
    setStartingDemo(true);
    setMessage('');
    try {
      const session = await startDemoSession();
      const metadata = { expiresAt: Date.now() + session.expires_in * 1000 };
      sessionStorage.setItem('neuroagent_token', session.access_token);
      sessionStorage.setItem('neuroagent_demo_session', JSON.stringify(metadata));
      setToken(session.access_token);
      setDemoSession(metadata);
      setMessage('Synthetic demo session started for 15 minutes. Cases belong only to this session.');
      navigate('/demo');
    } catch {
      setMessage('Unable to start the synthetic demo. Check the backend connection.');
    } finally { setStartingDemo(false); }
  };
  const saveToken = (event) => {
    event.preventDefault();
    if (!token.trim()) {
      setMessage('Enter a bearer token issued for your backend.');
      return;
    }
    sessionStorage.setItem('neuroagent_token', token.trim());
    sessionStorage.removeItem('neuroagent_demo_session');
    setDemoSession(null);
    setMessage('Session token saved for this tab.');
  };
  const clearToken = () => {
    sessionStorage.removeItem('neuroagent_token');
    sessionStorage.removeItem('neuroagent_demo_session');
    setDemoSession(null);
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
        <Box sx={{ mt: 3 }}>
          {demoConfig?.enabled && <Box sx={{ mb: 2 }}>
            <Typography variant="h6" component="h2">Explore a fictional example</Typography>
            <Typography variant="body2" sx={{ mb: 2 }}>Start a private demo session for 15 minutes. No account or API key is needed.</Typography>
            <Button variant="contained" onClick={startDemo} disabled={startingDemo || Boolean(demoSession)}>
              {startingDemo ? 'Starting demo…' : demoSession ? 'Demo session active' : 'Start synthetic demo'}
            </Button>
            {demoSession && <Button component={Link} to="/demo" sx={{ ml: 1 }}>Open synthetic example</Button>}
            {demoSession && <Button onClick={clearToken} sx={{ ml: 1 }}>End demo session</Button>}
          </Box>}
          <Button onClick={() => setAdvanced(!advanced)} aria-expanded={advanced}>Advanced API access</Button>
          {message && <Alert severity="info" sx={{ mt: 2 }} role="status">{message}</Alert>}
        </Box>
        {advanced && <Box component="form" onSubmit={saveToken} sx={{ mt: 2 }} aria-label="API session token">
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
        </Box>}
        <Box sx={{ my: 4 }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/diagnosis" element={demoSession
              ? <Alert severity="info">This session can run fictional examples only. <Link to="/demo">Open the synthetic demonstration</Link>.</Alert>
              : <DiagnosisPage />} />
            <Route path="/demo" element={<DemoAssessmentPage key={demoSession?.expiresAt || 'inactive'} config={demoConfig} active={Boolean(demoSession)} />} />
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
