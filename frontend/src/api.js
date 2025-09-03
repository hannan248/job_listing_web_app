import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method.toUpperCase(), config.url, config.data);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Job API functions
export const jobsAPI = {
  // Get all jobs with optional filters
  getJobs: async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      
      if (filters.search) params.append('search', filters.search);
      if (filters.job_type) params.append('job_type', filters.job_type);
      if (filters.location) params.append('location', filters.location);
      if (filters.tag) params.append('tag', filters.tag);
      if (filters.sort) params.append('sort', filters.sort);
      
      const response = await api.get(`/jobs?${params.toString()}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch jobs');
    }
  },

  // Get single job by ID
  getJob: async (id) => {
    try {
      const response = await api.get(`/jobs/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch job');
    }
  },

  // Create new job
  createJob: async (jobData) => {
    try {
      const response = await api.post('/jobs', jobData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to create job');
    }
  },

  // Update existing job
  updateJob: async (id, jobData) => {
    try {
      const response = await api.put(`/jobs/${id}`, jobData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to update job');
    }
  },

  // Delete job
  deleteJob: async (id) => {
    try {
      const response = await api.delete(`/jobs/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to delete job');
    }
  },

  // Get unique job types for dropdown
  getJobTypes: async () => {
    try {
      const response = await api.get('/jobs/job-types');
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch job types');
    }
  },

  // Get unique locations for dropdown
  getLocations: async () => {
    try {
      const response = await api.get('/jobs/locations');
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch locations');
    }
  },

  // Get all tags
  getTags: async () => {
    try {
      const response = await api.get('/jobs/tags');
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch tags');
    }
  },

  // Health check
  healthCheck: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      throw new Error('API health check failed');
    }
  }
};

export default api;