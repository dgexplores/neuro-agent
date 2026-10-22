import React, { useState } from 'react';
import {
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Box,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert
} from '@mui/material';
import DiagnosisResults from './DiagnosisResults';
import { submitDiagnosis } from '../services/api';

const DiagnosisPage = () => {
  const [formData, setFormData] = useState({
    age: '',
    gender: '',
    chiefComplaint: '',
    symptoms: '',
    medicalHistory: '',
    currentMedications: '',
    vitalSigns: {
      bloodPressure: '',
      heartRate: '',
      temperature: ''
    }
  });

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleInputChange = (field) => (event) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: event.target.value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: event.target.value
      }));
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const bp = formData.vitalSigns.bloodPressure.trim();
      if (bp && !/^\d{2,3}\/\d{2,3}$/.test(bp)) {
        throw new Error('Enter blood pressure as systolic/diastolic, for example 120/80.');
      }
      const diagnosisRequest = {
        patient_info: {
          age: parseInt(formData.age),
          gender: formData.gender,
          medical_history: formData.medicalHistory.split(',').map(s => s.trim()).filter(s => s),
          current_medications: formData.currentMedications.split(',').map(s => s.trim()).filter(s => s),
          allergies: []
        },
        symptoms: formData.symptoms.split(',').map(symptom => ({
          name: symptom.trim(),
          severity: 'moderate',
          duration_days: 7,
          description: ''
        })).filter(s => s.name),
        vital_signs: Object.fromEntries(Object.entries({
          bp_systolic: formData.vitalSigns.bloodPressure ? Number(formData.vitalSigns.bloodPressure.split('/')[0]) : null,
          bp_diastolic: formData.vitalSigns.bloodPressure ? Number(formData.vitalSigns.bloodPressure.split('/')[1]) : null,
          heart_rate: formData.vitalSigns.heartRate ? Number(formData.vitalSigns.heartRate) : null,
          temperature: formData.vitalSigns.temperature ? Number(formData.vitalSigns.temperature) : null
        }).filter(([, value]) => value !== null)),
        lab_results: {},
        imaging_studies: [],
        chief_complaint: formData.chiefComplaint,
        history_present_illness: formData.symptoms
      };

      const response = await submitDiagnosis(diagnosisRequest);
      setResults(response);
    } catch (err) {
      // Provide more detailed error message for debugging
      const errorMessage = err.message || 'Assessment failed. Check your session and try again.';
      setError(errorMessage);
      console.error('Diagnosis error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Educational assessment
      </Typography>

      <Card className="diagnosis-form">
        <CardContent>
          <form onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Age"
                  type="number"
                  inputProps={{ min: 0, max: 120, step: 1 }}
                  value={formData.age}
                  onChange={handleInputChange('age')}
                  required
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel id="gender-label">Gender</InputLabel>
                  <Select labelId="gender-label" label="Gender"
                    value={formData.gender}
                    onChange={handleInputChange('gender')}
                  >
                    <MenuItem value="male">Male</MenuItem>
                    <MenuItem value="female">Female</MenuItem>
                    <MenuItem value="other">Other</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Chief complaint"
                  multiline
                  rows={2}
                  value={formData.chiefComplaint}
                  onChange={handleInputChange('chiefComplaint')}
                  required
                  helperText="Describe the main symptoms using synthetic information."
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Symptoms"
                  multiline
                  rows={3}
                  value={formData.symptoms}
                  onChange={handleInputChange('symptoms')}
                  required
                  helperText="Separate symptoms with commas."
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Medical history"
                  value={formData.medicalHistory}
                  onChange={handleInputChange('medicalHistory')}
                  helperText="Separate items with commas."
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Current medications"
                  value={formData.currentMedications}
                  onChange={handleInputChange('currentMedications')}
                  helperText="Separate medication names with commas."
                />
              </Grid>

              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Blood pressure (systolic/diastolic)"
                  placeholder="120/80"
                  value={formData.vitalSigns.bloodPressure}
                  onChange={handleInputChange('vitalSigns.bloodPressure')}
                />
              </Grid>

              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Heart rate (bpm)"
                  type="number"
                  value={formData.vitalSigns.heartRate}
                  onChange={handleInputChange('vitalSigns.heartRate')}
                />
              </Grid>

              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Temperature (°C)"
                  type="number"
                  inputProps={{ step: 0.1 }}
                  value={formData.vitalSigns.temperature}
                  onChange={handleInputChange('vitalSigns.temperature')}
                />
              </Grid>

              <Grid item xs={12}>
                <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    disabled={loading}
                    sx={{ minWidth: 200 }}
                  >
                    {loading ? <CircularProgress size={24} /> : 'Run assessment'}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {results && <DiagnosisResults results={results} />}
    </Box>
  );
};

export default DiagnosisPage;
