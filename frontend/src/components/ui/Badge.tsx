import type { ReactNode } from 'react';

interface BadgeProps {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'purple';
  children: ReactNode;
  className?: string;
}

const variants = {
  default: 'bg-gray-100 text-gray-700',
  success: 'bg-green-50 text-green-700 ring-green-600/20',
  warning: 'bg-amber-50 text-amber-700 ring-amber-600/20',
  danger: 'bg-red-50 text-red-700 ring-red-600/20',
  info: 'bg-cyan-50 text-cyan-700 ring-cyan-600/20',
  purple: 'bg-purple-50 text-purple-700 ring-purple-600/20',
};

export function Badge({ variant = 'default', children, className = '' }: BadgeProps) {
  return (
    <span className={`badge ${variants[variant]} ring-1 ring-inset ${className}`}>
      {children}
    </span>
  );
}

const statusColors: Record<string, BadgeProps['variant']> = {
  NEW: 'info',
  CONTACTED: 'warning',
  DEMO: 'purple',
  NEGOTIATION: 'warning',
  WON: 'success',
  LOST: 'danger',
  PENDING: 'warning',
  COMPLETED: 'success',
  CANCELLED: 'default',
  LOW: 'default',
  MEDIUM: 'info',
  HIGH: 'warning',
  URGENT: 'danger',
};

export function StatusBadge({ status }: { status: string }) {
  const label = status.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  return <Badge variant={statusColors[status] || 'default'}>{label}</Badge>;
}

export function PriorityBadge({ priority }: { priority: string }) {
  const colors: Record<string, string> = {
    LOW: 'bg-gray-100 text-gray-600',
    MEDIUM: 'bg-blue-50 text-blue-700',
    HIGH: 'bg-amber-50 text-amber-700',
    URGENT: 'bg-red-50 text-red-700',
  };
  return (
    <span className={`badge ${colors[priority] || 'bg-gray-100 text-gray-600'}`}>
      {priority}
    </span>
  );
}
