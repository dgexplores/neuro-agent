import React, { useState, useEffect } from 'react';
import {
  Typography,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Box,
  Chip,
  Button,
  TextField,
  InputAdornment
} from '@mui/material';
import { Search, Assignment } from '@mui/icons-material';

const CaseHistoryPage = () => {
  const [cases, setCases] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);

  // Mock data for demonstration
  useEffect(() => {
    const mockCases = [
      {
        case_id: 'case-001',
        patient_age: 45,
        patient_gender: 'female',
        chief_complaint: '頭痛三天',
        diagnosis: '偏頭痛',
        confidence: 0.85,
        created_at: '2025-10-12T10:30:00Z',
        status: 'completed'
      },
      {
        case_id: 'case-002',
        patient_age: 67,
        patient_gender: 'male',
        chief_complaint: '左側肢體無力',
        diagnosis: '腦中風疑似',
        confidence: 0.92,
        created_at: '2025-10-11T14:20:00Z',
        status: 'completed'
      },
      {
        case_id: 'case-003',
        patient_age: 34,
        patient_gender: 'female',
        chief_complaint: '記憶力減退',
        diagnosis: '需進一步評估',
        confidence: 0.65,
        created_at: '2025-10-10T09:15:00Z',
        status: 'pending'
      }
    ];
    setCases(mockCases);
  }, []);

  const filteredCases = cases.filter(case_ =>
    case_.chief_complaint.toLowerCase().includes(searchTerm.toLowerCase()) ||
    case_.diagnosis.toLowerCase().includes(searchTerm.toLowerCase()) ||
    case_.case_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'pending': return 'warning';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed': return '已完成';
      case 'pending': return '處理中';
      case 'failed': return '失敗';
      default: return '未知';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        病例記錄
      </Typography>

      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          placeholder="搜尋病例..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      {filteredCases.length === 0 ? (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <Assignment sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              目前沒有病例記錄
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              開始診斷分析來建立第一個病例記錄
            </Typography>
            <Button variant="contained" href="/diagnosis">
              開始診斷
            </Button>
          </CardContent>
        </Card>
      ) : (
        <List>
          {filteredCases.map((case_, index) => (
            <Card key={case_.case_id} sx={{ mb: 2 }}>
              <ListItem>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="h6">
                        {case_.chief_complaint}
                      </Typography>
                      <Box>
                        <Chip
                          label={getStatusText(case_.status)}
                          color={getStatusColor(case_.status)}
                          size="small"
                          sx={{ mr: 1 }}
                        />
                        <Chip
                          label={`可信度: ${(case_.confidence * 100).toFixed(0)}%`}
                          color={getConfidenceColor(case_.confidence)}
                          size="small"
                        />
                      </Box>
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        病例編號: {case_.case_id}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        患者: {case_.patient_age}歲 {case_.patient_gender === 'male' ? '男性' : '女性'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        診斷結果: {case_.diagnosis}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        建立時間: {formatDate(case_.created_at)}
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            </Card>
          ))}
        </List>
      )}
    </Box>
  );
};

export default CaseHistoryPage;
