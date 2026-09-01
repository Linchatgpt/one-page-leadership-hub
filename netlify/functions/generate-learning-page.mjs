import api from './api.mjs';
export default (event) => api({ ...event, path: '/generate-learning-page' });
