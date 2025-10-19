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

    // Re-throw error instead of returning mock data
    // This allows proper error handling in the UI
    throw new Error(
      `無法連接到診斷服務: ${error.response?.status || error.message}。` +
      `請確保後端服務正在運行且配置正確。`
    );
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
