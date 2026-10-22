import React from 'react';
import { Alert, Typography, Card, CardContent, Grid, Box, Button, Link } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const features = [
  { title: 'Structured assessment input', description: 'Submit symptoms, patient context, and optional clinical observations through the Python API.' },
  { title: 'AWS Bedrock integration', description: 'Explore how a language model turns structured input into assessment suggestions and follow-up questions.' },
  { title: 'Saved case lookup', description: 'Retrieve a persisted assessment by its case ID using the account that created it.' },
  { title: 'Application engineering', description: 'Explore validated API requests, authenticated case access, persistence, automated tests, and AWS deployment configuration.' }
];

const HomePage = () => {
  const navigate = useNavigate();
  return (
    <Box>
      <Box sx={{ textAlign: 'center', mb: 5 }}>
        <Typography variant="h2" component="h1" gutterBottom color="primary">NeuroAgent</Typography>
        <Typography variant="h5" color="text.secondary" gutterBottom>AI assessment workflow · Educational portfolio prototype</Typography>
        <Typography sx={{ mb: 3, maxWidth: 680, mx: 'auto' }}>
          A Python, FastAPI, and React application for exploring structured AI workflows,
          AWS integration, and authenticated case storage. Use synthetic examples to
          examine the application from input validation to saved results.
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
          <Button variant="contained" size="large" onClick={() => navigate('/diagnosis')}>Try an assessment</Button>
          <Button variant="outlined" size="large" onClick={() => navigate('/history')}>Look up a saved case</Button>
        </Box>
      </Box>
      <Alert severity="info" sx={{ mb: 4 }}>
        This prototype has not been clinically validated. Its outputs are for learning
        and demonstration and must not guide diagnosis or treatment. Use synthetic data.
      </Alert>
      <Grid container spacing={3}>
        {features.map((feature) => (
          <Grid item xs={12} md={6} key={feature.title}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>{feature.title}</Typography>
                <Typography color="text.secondary">{feature.description}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      <Box component="footer" sx={{ mt: 5, pt: 3, borderTop: 1, borderColor: 'divider' }}>
        <Typography variant="body2" color="text.secondary">
          Portfolio extension for <Link href="https://github.com/dgexplores">dgexplores</Link>.
          {' '}Based on the <Link href="https://github.com/thc1006/neuro-agent">upstream NeuroAgent project</Link>.
        </Typography>
      </Box>
    </Box>
  );
};

export default HomePage;
