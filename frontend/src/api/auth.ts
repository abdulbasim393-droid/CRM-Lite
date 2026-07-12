import apiClient from './client';

export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post('/auth/login/', { email, password }),

  register: (data: {
    email: string;
    password: string;
    confirm_password: string;
    first_name: string;
    last_name: string;
    role?: string;
  }) => apiClient.post('/auth/register/', data),

  logout: (refresh: string) =>
    apiClient.post('/auth/logout/', { refresh }),

  refresh: (refresh: string) =>
    apiClient.post('/auth/refresh/', { refresh }),

  me: () => apiClient.get('/auth/me/'),
};
