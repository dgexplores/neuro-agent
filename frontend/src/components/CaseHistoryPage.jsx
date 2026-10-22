import React, { useState } from 'react';
import {
  Alert, Box, Button, Card, CardContent, CircularProgress,
  List, ListItem, ListItemText, TextField, Typography
} from '@mui/material';
import { getCase } from '../services/api';

const CaseHistoryPage = () => {
  const [caseId, setCaseId] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const lookupCase = async (event) => {
    event.preventDefault();
    const requestedId = caseId.trim();
    if (!requestedId || loading) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      setResult(await getCase(requestedId));
    } catch (failure) {
      const status = failure.response?.status;
      setError(status === 404
        ? 'Case not found. Check the ID and use the account that created it.'
        : status === 401 || status === 403
          ? 'Sign in with a valid access token to retrieve your saved case.'
          : 'Unable to retrieve this case. Check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderItems = (title, values) => Array.isArray(values) && values.length > 0 && (
    <Box sx={{ mt: 2 }}>
      <Typography variant="h6">{title}</Typography>
      <List dense>
        {values.map((value, index) => (
          <ListItem key={index} disableGutters>
            <ListItemText primary={typeof value === 'string' ? value : JSON.stringify(value)} />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>Saved cases</Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Enter the case ID returned by an assessment to retrieve its stored result.
        Only cases belonging to your authenticated account can be retrieved.
      </Typography>
      <Box component="form" onSubmit={lookupCase} sx={{ mb: 3 }}>
        <TextField
          fullWidth label="Case ID" value={caseId}
          onChange={(event) => setCaseId(event.target.value)}
          disabled={loading} autoComplete="off" required
        />
        <Button type="submit" variant="contained" disabled={loading || !caseId.trim()} sx={{ mt: 2 }}>
          {loading ? 'Looking up case…' : 'Find case'}
        </Button>
        {loading && <CircularProgress size={24} aria-label="Loading case" sx={{ ml: 2 }} />}
      </Box>
      {error && <Alert severity="error" role="alert">{error}</Alert>}
      {!result && !loading && !error && (
        <Typography color="text.secondary">No case loaded. Save the case ID after submitting an assessment.</Typography>
      )}
      {result && (
        <Card aria-label="Saved case result">
          <CardContent>
            <Typography variant="h5">Case {result.case_id}</Typography>
            {result.timestamp && <Typography color="text.secondary">Recorded: {result.timestamp}</Typography>}
            <Alert severity="info" sx={{ my: 2 }}>
              Educational prototype output. Model confidence scores are not validated clinical accuracy.
            </Alert>
            <Typography variant="h6">Assessment output</Typography>
            <List>
              {(Array.isArray(result.diagnosis) ? result.diagnosis : []).map((item, index) => (
                <ListItem key={index} disableGutters>
                  <ListItemText primary={item.condition} secondary={item.reasoning} />
                </ListItem>
              ))}
            </List>
            {renderItems('Recommendations', result.recommendations)}
            {renderItems('Risk factors', result.risk_factors)}
            {renderItems('Next steps', result.next_steps)}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default CaseHistoryPage;
