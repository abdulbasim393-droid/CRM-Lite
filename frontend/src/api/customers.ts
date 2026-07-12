import apiClient from './client';
import type { Customer } from '../types';

export const customersApi = {
  list: () => apiClient.get<Customer[]>('/customers/'),
  retrieve: (id: string) => apiClient.get<Customer>(`/customers/${id}/`),
};
