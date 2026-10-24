import React, { useState } from 'react';
import { Alert, Box, Button, Card, CardContent, CircularProgress, Typography } from '@mui/material';
import DiagnosisResults from './DiagnosisResults';
import { submitDemoAssessment } from '../services/api';

const DemoAssessmentPage = ({ config, active }) => {
  const [loading, setLoading] = useState(false);
  const [attempted, setAttempted] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const runExample = async (sampleId) => {
    if (loading || attempted || !active) return;
    setLoading(true);
    setAttempted(true);
    setError('');
    setResult(null);
    try {
      setResult(await submitDemoAssessment(sampleId));
    } catch (failure) {
      setError(failure.message || 'The assessment service is unavailable.');
    } finally {
      setLoading(false);
    }
  };

  if (!config?.enabled) return <Alert severity="info">The synthetic demo is not enabled on this backend.</Alert>;
  return <Box>
    <Typography variant="h4" component="h1" gutterBottom>Synthetic demonstration</Typography>
    <Alert severity="info" sx={{ mb: 3 }}>
      These examples are invented for this portfolio. One real model attempt is allowed per session,
      including failed calls, with ten attempts across the site per UTC day. This is an educational
      prototype and must not guide diagnosis or treatment.
    </Alert>
    {!active && <Alert severity="warning" sx={{ mb: 2 }}>Start a synthetic demo session above to run an example.</Alert>}
    {(config.samples || []).map((sample) => <Card key={sample.id} sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6">{sample.name}</Typography>
        <Typography sx={{ my: 1 }}>{sample.summary}</Typography>
        <Typography variant="body2" color="text.secondary">
          Age {sample.request.patient_info.age} · {sample.request.patient_info.gender} · Symptoms:
          {' '}{sample.request.symptoms.map((symptom) => symptom.name).join(', ')}
        </Typography>
        <Button variant="contained" sx={{ mt: 2 }} disabled={!active || loading || attempted}
          onClick={() => runExample(sample.id)}>
          {loading ? 'Running example…' : 'Run fictional example'}
        </Button>
      </CardContent>
    </Card>)}
    {loading && <CircularProgress aria-label="Running synthetic assessment" />}
    {error && <Alert severity="error" role="alert">{error}</Alert>}
    {result && <DiagnosisResults results={result} />}
  </Box>;
};

export default DemoAssessmentPage;
