import React from 'react';
import { 
  Typography, 
  Card, 
  CardContent, 
  Grid, 
  Box,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Psychology,
  LocalHospital,
  Analytics,
  Security,
  CheckCircle
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <Psychology />,
      title: 'AI智能診斷',
      description: '基於AWS Bedrock的多模態神經疾病分析'
    },
    {
      icon: <LocalHospital />,
      title: '循證醫學',
      description: '整合最新臨床指南和治療建議'
    },
    {
      icon: <Analytics />,
      title: '風險評估',
      description: '智能風險分層和預後評估'
    },
    {
      icon: <Security />,
      title: '安全可靠',
      description: '符合醫療資料安全標準'
    }
  ];

  return (
    <Box>
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography variant="h2" component="h1" gutterBottom color="primary">
          NeuroAgent
        </Typography>
        <Typography variant="h5" color="text.secondary" gutterBottom>
          AI驅動的神經疾病診療輔助系統
        </Typography>
        <Typography variant="body1" sx={{ mb: 4, maxWidth: 600, mx: 'auto' }}>
          結合AWS AI Agent技術與神經醫學專業知識，為醫療專業人員提供智能診斷支援，
          提升診療效率和準確性。
        </Typography>

        <Button 
          variant="contained" 
          size="large" 
          onClick={() => navigate('/diagnosis')}
          sx={{ mr: 2 }}
        >
          開始診斷
        </Button>
        <Button 
          variant="outlined" 
          size="large"
          onClick={() => navigate('/history')}
        >
          查看病例
        </Button>
      </Box>

      <Grid container spacing={4} sx={{ mb: 6 }}>
        {features.map((feature, index) => (
          <Grid item xs={12} md={6} key={index}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {feature.icon}
                  <Typography variant="h6" sx={{ ml: 1 }}>
                    {feature.title}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            系統優勢
          </Typography>
          <List>
            <ListItem>
              <ListItemIcon>
                <CheckCircle color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="企業級AI技術"
                secondary="採用Amazon Bedrock AgentCore，提供高可靠性和擴展性"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircle color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="多模態分析"
                secondary="同時處理文本病歷、影像資料和實驗室檢查結果"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircle color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="個人化建議"
                secondary="根據患者特徵提供客製化的診斷建議和治療方案"
              />
            </ListItem>
          </List>
        </CardContent>
      </Card>
    </Box>
  );
};

export default HomePage;
