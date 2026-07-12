export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'ADMIN' | 'SALES_MANAGER' | 'SALES_EXECUTIVE';
  created_at: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginResponse {
  message: string;
  user: User;
  access: string;
  refresh: string;
}

export interface LeadSource {
  id: string;
  name: string;
  description: string;
  is_active: boolean;
}

export interface Lead {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  company: string;
  job_title: string;
  website: string;
  source: string;
  source_name: string;
  status: LeadStatus;
  priority: LeadPriority;
  estimated_value: string;
  assigned_to: string | null;
  assigned_to_name: string | null;
  created_by: string | null;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export type LeadStatus = 'NEW' | 'CONTACTED' | 'DEMO' | 'NEGOTIATION' | 'WON' | 'LOST';
export type LeadPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
export type NoteType = 'CALL' | 'WHATSAPP' | 'MEETING' | 'DEMO' | 'OBJECTION' | 'OTHER';
export type FollowUpStatus = 'PENDING' | 'COMPLETED' | 'CANCELLED';
export type EntityType = 'LEAD' | 'LEAD_NOTE' | 'CUSTOMER' | 'FOLLOW_UP' | 'USER';
export type ActionType = 'CREATED' | 'UPDATED' | 'DELETED' | 'CONVERTED' | 'COMPLETED' | 'ASSIGNED';

export interface LeadNote {
  id: string;
  lead: string;
  note_type: NoteType;
  note_text: string;
  created_by: string;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

export interface Customer {
  id: string;
  lead: string;
  first_name: string;
  last_name: string;
  phone: string;
  email: string;
  company: string;
  address: string;
  created_by: string;
  created_by_name: string;
  converted_at: string;
  created_at: string;
  updated_at: string;
}

export interface FollowUp {
  id: string;
  lead: string;
  assigned_to: string;
  assigned_to_name: string;
  follow_up_at: string;
  purpose: string;
  status: FollowUpStatus;
  outcome: string;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ActivityLog {
  id: string;
  entity_type: EntityType;
  entity_id: string;
  action: ActionType;
  old_value: Record<string, unknown> | null;
  new_value: Record<string, unknown> | null;
  performed_by: string;
  performed_by_name: string;
  created_at: string;
}

export interface DashboardData {
  total_leads: number;
  converted_leads: number;
  lost_leads: number;
  today_followups: number;
  overdue_followups: number;
  pipeline_value: number;
  conversion_rate: number;
}

export interface UserReport {
  user_id: string;
  user_name: string;
  total_leads: number;
  won_leads: number;
  lost_leads: number;
  customers: number;
  pending_followups: number;
}

export interface StatusReport {
  status: string;
  label: string;
  count: number;
}

export interface SourceReport {
  source_id: string;
  source_name: string;
  count: number;
}

export interface DateReport {
  start_date: string;
  end_date: string;
  leads_created: number;
  customers_converted: number;
  followups_created: number;
  leads_by_status: Record<string, number>;
  pipeline_value: number;
}
