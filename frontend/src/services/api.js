import axios from 'axios';

// Configure this application to use your own backend in every build mode.
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
    // Read the operator-supplied session token; no credential is bundled.
    const token = sessionStorage.getItem('neuroagent_token');

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
    const status = error.response?.status;
    const messages = {
      401: 'Your session token is invalid or expired. Save a new token and retry.',
      403: 'Save a bearer token in the API session panel before submitting.',
      422: 'Check the required fields and numeric values, then retry.',
      502: 'The model returned an invalid response. Please retry.',
      503: 'The backend cannot reach its model or storage service. Check the backend configuration.'
    };
    throw new Error(messages[status] || 'Unable to reach the assessment service. Check your backend URL and connection.');
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

export const getCase = async (caseId) => {
  const response = await api.get(`/api/v1/cases/${encodeURIComponent(caseId)}`);
  return response.data;
};

export default api;
