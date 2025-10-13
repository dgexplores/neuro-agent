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

    try {
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
        vital_signs: {
          bp_systolic: formData.vitalSigns.bloodPressure ? parseInt(formData.vitalSigns.bloodPressure.split('/')[0]) : null,
          bp_diastolic: formData.vitalSigns.bloodPressure ? parseInt(formData.vitalSigns.bloodPressure.split('/')[1]) : null,
          heart_rate: formData.vitalSigns.heartRate ? parseInt(formData.vitalSigns.heartRate) : null,
          temperature: formData.vitalSigns.temperature ? parseFloat(formData.vitalSigns.temperature) : null
        },
        lab_results: {},
        imaging_studies: [],
        chief_complaint: formData.chiefComplaint,
        history_present_illness: formData.symptoms
      };

      const response = await submitDiagnosis(diagnosisRequest);
      setResults(response);
    } catch (err) {
      setError('診斷分析時發生錯誤，請稍後再試');
      console.error('Diagnosis error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        神經疾病診斷分析
      </Typography>

      <Card className="diagnosis-form">
        <CardContent>
          <form onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="年齡"
                  type="number"
                  value={formData.age}
                  onChange={handleInputChange('age')}
                  required
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel>性別</InputLabel>
                  <Select
                    value={formData.gender}
                    onChange={handleInputChange('gender')}
                  >
                    <MenuItem value="male">男性</MenuItem>
                    <MenuItem value="female">女性</MenuItem>
                    <MenuItem value="other">其他</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="主訴"
                  multiline
                  rows={2}
                  value={formData.chiefComplaint}
                  onChange={handleInputChange('chiefComplaint')}
                  required
                  helperText="請描述患者的主要症狀或不適"
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="症狀描述"
                  multiline
                  rows={3}
                  value={formData.symptoms}
                  onChange={handleInputChange('symptoms')}
                  required
                  helperText="請詳細描述症狀，以逗號分隔多個症狀"
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="既往病史"
                  value={formData.medicalHistory}
                  onChange={handleInputChange('medicalHistory')}
                  helperText="以逗號分隔多個病史"
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="目前用藥"
                  value={formData.currentMedications}
                  onChange={handleInputChange('currentMedications')}
                  helperText="以逗號分隔多個藥物"
                />
              </Grid>

              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="血壓 (收縮壓/舒張壓)"
                  placeholder="120/80"
                  value={formData.vitalSigns.bloodPressure}
                  onChange={handleInputChange('vitalSigns.bloodPressure')}
                />
              </Grid>

              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="心率 (次/分)"
                  type="number"
                  value={formData.vitalSigns.heartRate}
                  onChange={handleInputChange('vitalSigns.heartRate')}
                />
              </Grid>

              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="體溫 (°C)"
                  type="number"
                  step="0.1"
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
                    {loading ? <CircularProgress size={24} /> : '開始診斷分析'}
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
