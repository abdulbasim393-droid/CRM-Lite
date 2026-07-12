import apiClient from './client';
import type { DateReport, SourceReport, StatusReport, UserReport } from '../types';

export const reportsApi = {
  userWise: () =>
    apiClient.get<UserReport[]>('/reports/user-wise/'),

  statusWise: () =>
    apiClient.get<StatusReport[]>('/reports/status-wise/'),

  sourceWise: () =>
    apiClient.get<SourceReport[]>('/reports/source-wise/'),

  dateWise: (start: string, end: string) =>
    apiClient.get<DateReport>('/reports/date-wise/', { params: { start, end } }),
};
