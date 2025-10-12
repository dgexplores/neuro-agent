import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  List,
  ListItem,
  ListItemText,
  LinearProgress,
  Grid,
  Divider
} from '@mui/material';
import {
  Assessment,
  Warning,
  Lightbulb,
  NavigateNext
} from '@mui/icons-material';

const DiagnosisResults = ({ results }) => {
  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const getConfidenceText = (confidence) => {
    if (confidence >= 0.8) return '高';
    if (confidence >= 0.6) return '中';
    return '低';
  };

  return (
    <Card className="results-panel" sx={{ mt: 3 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom color="primary">
          <Assessment sx={{ mr: 1, verticalAlign: 'middle' }} />
          診斷分析結果
        </Typography>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          病例編號: {results.case_id}
        </Typography>

        {/* Overall Confidence */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            整體可信度: {getConfidenceText(results.confidence)}
          </Typography>
          <LinearProgress
            variant="determinate"
            value={results.confidence * 100}
            color={getConfidenceColor(results.confidence)}
            sx={{ height: 8, borderRadius: 4 }}
          />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {(results.confidence * 100).toFixed(1)}%
          </Typography>
        </Box>

        <Grid container spacing={3}>
          {/* Differential Diagnoses */}
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              <Assessment sx={{ mr: 1, verticalAlign: 'middle' }} />
              鑑別診斷
            </Typography>
            <List>
              {results.diagnosis.map((diagnosis, index) => (
                <ListItem key={index} className="diagnosis-card" sx={{ mb: 2, p: 2 }}>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="subtitle1">
                          {diagnosis.condition}
                        </Typography>
                        <Chip
                          label={`${(diagnosis.confidence * 100).toFixed(0)}%`}
                          color={getConfidenceColor(diagnosis.confidence)}
                          size="small"
                        />
                      </Box>
                    }
                    secondary={diagnosis.reasoning}
                  />
                </ListItem>
              ))}
            </List>
          </Grid>

          {/* Recommendations */}
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              <Lightbulb sx={{ mr: 1, verticalAlign: 'middle' }} />
              建議
            </Typography>
            <List dense>
              {results.recommendations.map((recommendation, index) => (
                <ListItem key={index}>
                  <ListItemText primary={recommendation} />
                </ListItem>
              ))}
            </List>
          </Grid>

          {/* Risk Factors */}
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              <Warning sx={{ mr: 1, verticalAlign: 'middle' }} />
              風險因子
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {results.risk_factors.map((risk, index) => (
                <Chip
                  key={index}
                  label={risk}
                  variant="outlined"
                  color="warning"
                  size="small"
                />
              ))}
            </Box>
          </Grid>

          {/* Next Steps */}
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              <NavigateNext sx={{ mr: 1, verticalAlign: 'middle' }} />
              後續步驟
            </Typography>
            <List dense>
              {results.next_steps.map((step, index) => (
                <ListItem key={index}>
                  <ListItemText primary={step} />
                </ListItem>
              ))}
            </List>
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        <Typography variant="body2" color="text.secondary" align="center">
          ⚠️ 此診斷分析僅供參考，實際診療請務必諮詢專業醫師
        </Typography>
      </CardContent>
    </Card>
  );
};

export default DiagnosisResults;
