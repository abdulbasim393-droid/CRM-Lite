import { useEffect, useState } from 'react';
import { Card, CardBody } from '../components/ui/Card';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { activityApi } from '../api/activity';
import type { ActivityLog } from '../types';
import {
  PlusCircle, Edit3, Trash2, Repeat, CheckCircle2, UserPlus,
  FileText, Briefcase, Users, CalendarCheck,
} from 'lucide-react';

const actionIcons: Record<string, typeof PlusCircle> = {
  CREATED: PlusCircle, UPDATED: Edit3, DELETED: Trash2,
  CONVERTED: Repeat, COMPLETED: CheckCircle2, ASSIGNED: UserPlus,
};

const actionColors: Record<string, string> = {
  CREATED: 'text-green-600 bg-green-50',
  UPDATED: 'text-blue-600 bg-blue-50',
  DELETED: 'text-red-600 bg-red-50',
  CONVERTED: 'text-purple-600 bg-purple-50',
  COMPLETED: 'text-emerald-600 bg-emerald-50',
  ASSIGNED: 'text-amber-600 bg-amber-50',
};

const entityIcons: Record<string, typeof Briefcase> = {
  LEAD: Briefcase, LEAD_NOTE: FileText, CUSTOMER: Users,
  FOLLOW_UP: CalendarCheck, USER: UserPlus,
};

export function ActivityLogsPage() {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    activityApi.list()
      .then((res) => setLogs(res.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <Card>
      <CardBody>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Activity Logs</h2>
        {logs.length === 0 ? (
          <div className="text-center py-12 text-gray-500">No activity recorded yet.</div>
        ) : (
          <div className="relative pl-8 space-y-0 before:absolute before:left-[17px] before:top-3 before:bottom-3 before:w-0.5 before:bg-gray-100">
            {logs.map((log) => {
              const ActionIcon = actionIcons[log.action] || PlusCircle;
              const EntityIcon = entityIcons[log.entity_type] || Briefcase;
              return (
                <div key={log.id} className="relative pb-6 group">
                  <div className={`absolute -left-[26px] top-0 p-1.5 rounded-xl ${actionColors[log.action] || 'bg-gray-50 text-gray-600'}`}>
                    <ActionIcon size={14} />
                  </div>
                  <div className="ml-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-900 capitalize">
                        {log.action.replace(/_/g, ' ').toLowerCase()}
                      </span>
                      <EntityIcon size={14} className="text-gray-400" />
                      <span className="text-sm text-gray-600 capitalize">
                        {log.entity_type.replace(/_/g, ' ').toLowerCase()}
                      </span>
                    </div>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {log.performed_by_name} · {new Date(log.created_at).toLocaleString()}
                    </p>
                    {log.new_value && (
                      <p className="text-xs text-gray-500 mt-1 bg-gray-50 rounded-lg p-2 inline-block">
                        {JSON.stringify(log.new_value).substring(0, 120)}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardBody>
    </Card>
  );
}
