import apiClient from './client';
import type { FollowUp } from '../types';

export const followupsApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<FollowUp[]>('/followups/', { params }),

  retrieve: (id: string) =>
    apiClient.get<FollowUp>(`/followups/${id}/`),

  create: (data: Partial<FollowUp>) =>
    apiClient.post<FollowUp>('/followups/', data),

  update: (id: string, data: Partial<FollowUp>) =>
    apiClient.patch<FollowUp>(`/followups/${id}/`, data),

  delete: (id: string) =>
    apiClient.delete(`/followups/${id}/`),

  complete: (id: string, outcome: string) =>
    apiClient.patch<FollowUp>(`/followups/${id}/complete/`, { outcome }),
};
