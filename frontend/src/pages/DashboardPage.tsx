import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Users, UserCheck, UserX, Target, Building2, TrendingUp, DollarSign,
  Calendar, Clock, CheckCircle2, AlertCircle, ArrowUp, ArrowDown,
} from 'lucide-react';
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import { Card, CardBody, CardHeader } from '../components/ui/Card';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { dashboardApi } from '../api/dashboard';
import { reportsApi } from '../api/reports';
import type { DashboardData, StatusReport } from '../types';

export function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [statusData, setStatusData] = useState<StatusReport[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      dashboardApi.get(),
      reportsApi.statusWise(),
    ]).then(([dash, status]) => {
      setData(dash.data);
      setStatusData(status.data);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;

  const kpiCards = [
    { label: 'Total Leads', value: data?.total_leads ?? 0, icon: Users, color: 'text-blue-600', bg: 'bg-blue-50', desc: 'All time' },
    { label: 'Converted', value: data?.converted_leads ?? 0, icon: UserCheck, color: 'text-green-600', bg: 'bg-green-50', desc: 'Became customers' },
    { label: 'Lost Leads', value: data?.lost_leads ?? 0, icon: UserX, color: 'text-red-600', bg: 'bg-red-50', desc: 'Opportunities lost' },
    { label: 'Conversion Rate', value: `${data?.conversion_rate ?? 0}%`, icon: Target, color: 'text-purple-600', bg: 'bg-purple-50', desc: 'Lead to customer' },
    { label: 'Pipeline Value', value: `$${(data?.pipeline_value ?? 0).toLocaleString()}`, icon: DollarSign, color: 'text-emerald-600', bg: 'bg-emerald-50', desc: 'Active deals' },
    { label: 'Today\'s Follow-ups', value: data?.today_followups ?? 0, icon: Calendar, color: 'text-cyan-600', bg: 'bg-cyan-50', desc: 'Scheduled today' },
    { label: 'Overdue', value: data?.overdue_followups ?? 0, icon: AlertCircle, color: 'text-orange-600', bg: 'bg-orange-50', desc: 'Past due' },
  ];

  const STATUS_COLORS: Record<string, string> = {
    NEW: '#3B82F6', CONTACTED: '#F59E0B', DEMO: '#8B5CF6',
    NEGOTIATION: '#F97316', WON: '#16A34A', LOST: '#DC2626',
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {kpiCards.map((kpi) => (
          <Card key={kpi.label}>
            <CardBody>
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-gray-500 font-medium">{kpi.label}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{kpi.value}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{kpi.desc}</p>
                </div>
                <div className={`p-3 rounded-xl ${kpi.bg} ${kpi.color}`}>
                  <kpi.icon size={22} />
                </div>
              </div>
            </CardBody>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><h3 className="font-semibold text-gray-900">Leads by Status</h3></CardHeader>
          <CardBody>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={statusData} dataKey="count" nameKey="label" cx="50%" cy="50%" outerRadius={90} innerRadius={50}>
                  {statusData.map((entry) => (
                    <Cell key={entry.status} fill={STATUS_COLORS[entry.status] || '#9CA3AF'} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>

        <Card>
          <CardHeader><h3 className="font-semibold text-gray-900">Quick Actions</h3></CardHeader>
          <CardBody className="space-y-3">
            <button onClick={() => navigate('/leads')} className="w-full text-left p-4 rounded-xl bg-blue-50 hover:bg-blue-100 transition-colors">
              <p className="font-medium text-blue-700">View All Leads</p>
              <p className="text-sm text-blue-600/70 mt-0.5">Manage your lead pipeline</p>
            </button>
            <button onClick={() => navigate('/followups')} className="w-full text-left p-4 rounded-xl bg-amber-50 hover:bg-amber-100 transition-colors">
              <p className="font-medium text-amber-700">Pending Follow-ups</p>
              <p className="text-sm text-amber-600/70 mt-0.5">{data?.overdue_followups} overdue, {data?.today_followups} today</p>
            </button>
            <button onClick={() => navigate('/reports')} className="w-full text-left p-4 rounded-xl bg-green-50 hover:bg-green-100 transition-colors">
              <p className="font-medium text-green-700">View Reports</p>
              <p className="text-sm text-green-600/70 mt-0.5">Analyze team performance</p>
            </button>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
