/**
 * Frontend configuration - environment aware
 */

const config = {
  apiBaseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
};

export default config;
