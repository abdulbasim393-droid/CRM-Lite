import apiClient from './client';
import type { ActivityLog } from '../types';

export const activityApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<ActivityLog[]>('/activity/activity-logs/', { params }),
};
