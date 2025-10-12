import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    // For hackathon demo, use a demo token
    const token = 'REDACTED';
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      console.error('Unauthorized access');
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const submitDiagnosis = async (diagnosisRequest) => {
  try {
    const response = await api.post('/api/v1/diagnosis', diagnosisRequest);
    return response.data;
  } catch (error) {
    console.error('Diagnosis submission error:', error);

    // Return mock response for demo purposes
    return {
      case_id: `demo-case-${Date.now()}`,
      diagnosis: [
        {
          condition: '偏頭痛 (Migraine)',
          confidence: 0.85,
          reasoning: '基於症狀模式和患者年齡，偏頭痛是最可能的診斷'
        },
        {
          condition: '緊張性頭痛 (Tension Headache)', 
          confidence: 0.65,
          reasoning: '考慮到壓力因素和頭痛特徵'
        },
        {
          condition: '叢集性頭痛 (Cluster Headache)',
          confidence: 0.30,
          reasoning: '症狀模式不太符合，但需要排除'
        }
      ],
      confidence: 0.82,
      recommendations: [
        '建議進行神經學檢查',
        '考慮使用三叉神經止痛劑治療',
        '評估生活型態觸發因子',
        '考慮預防性治療的必要性'
      ],
      risk_factors: [
        '女性患者',
        '育齡期',
        '壓力相關因素'
      ],
      next_steps: [
        '安排追蹤門診',
        '頭痛日記記錄',
        '必要時安排腦部影像檢查',
        '評估藥物治療反應'
      ],
      timestamp: new Date().toISOString()
    };
  }
};

export const uploadMedicalImage = async (imageFile) => {
  const formData = new FormData();
  formData.append('file', imageFile);

  const response = await api.post('/api/v1/upload-image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const getCaseHistory = async () => {
  const response = await api.get('/api/v1/cases');
  return response.data;
};

export const getCase = async (caseId) => {
  const response = await api.get(`/api/v1/cases/${caseId}`);
  return response.data;
};

export default api;
