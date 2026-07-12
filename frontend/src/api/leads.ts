import apiClient from './client';
import type { Lead, LeadSource } from '../types';

export const leadsApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<Lead[]>('/leads/leads/', { params }),

  retrieve: (id: string) =>
    apiClient.get<Lead>(`/leads/leads/${id}/`),

  create: (data: Partial<Lead>) =>
    apiClient.post<Lead>('/leads/leads/', data),

  update: (id: string, data: Partial<Lead>) =>
    apiClient.patch<Lead>(`/leads/leads/${id}/`, data),

  delete: (id: string) =>
    apiClient.delete(`/leads/leads/${id}/`),

  convert: (id: string) =>
    apiClient.post(`/leads/leads/${id}/convert/`),
};

export const leadSourcesApi = {
  list: () =>
    apiClient.get<LeadSource[]>('/leads/lead-sources/'),

  create: (data: Partial<LeadSource>) =>
    apiClient.post<LeadSource>('/leads/lead-sources/', data),

  update: (id: string, data: Partial<LeadSource>) =>
    apiClient.patch<LeadSource>(`/leads/lead-sources/${id}/`, data),

  delete: (id: string) =>
    apiClient.delete(`/leads/lead-sources/${id}/`),
};

export const leadNotesApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get('/leads/lead-notes/', { params }),

  create: (data: { lead: string; note_type: string; note_text: string }) =>
    apiClient.post('/leads/lead-notes/', data),

  update: (id: string, data: { note_type?: string; note_text?: string }) =>
    apiClient.patch(`/leads/lead-notes/${id}/`, data),

  delete: (id: string) =>
    apiClient.delete(`/leads/lead-notes/${id}/`),
};
