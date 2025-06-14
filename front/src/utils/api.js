import axios from 'axios';

const baseURL = process.env.NODE_ENV === 'production'
  ? 'https://proyecto-lsae-production.up.railway.app/api'
  : '/api';

export const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' }
});
