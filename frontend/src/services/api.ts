import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const uploadStatement = async (file: File, broker: string) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${API_URL}/upload?broker=${broker}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const confirmMapping = async (filename: string, mapping: Record<string, string>) => {
  const response = await axios.post(`${API_URL}/confirm-mapping/${filename}`, { mapping });
  return response.data;
};

export const getTransactions = async () => {
  const response = await axios.get(`${API_URL}/transactions`);
  return response.data;
};

export const getResults = async () => {
  const response = await axios.get(`${API_URL}/results`);
  return response.data;
};
