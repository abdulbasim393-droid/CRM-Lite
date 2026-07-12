import { useEffect, useState } from 'react';
import { Card, CardBody, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { reportsApi } from '../api/reports';
import type { UserReport, StatusReport, SourceReport, DateReport } from '../types';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
} from 'recharts';
import { Download, Users, BarChart3, Globe, Calendar } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export function ReportsPage() {
  const [userData, setUserData] = useState<UserReport[]>([]);
  const [statusData, setStatusData] = useState<StatusReport[]>([]);
  const [sourceData, setSourceData] = useState<SourceReport[]>([]);
  const [dateData, setDateData] = useState<DateReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [startDate, setStartDate] = useState(() => new Date(Date.now() - 30 * 86400000).toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState(() => new Date().toISOString().split('T')[0]);
  const { isAdmin, isManager } = useAuth();

  const fetchReports = async () => {
    setLoading(true);
    try {
      const [userRes, statusRes, sourceRes, dateRes] = await Promise.all([
        reportsApi.userWise().catch(() => ({ data: [] as UserReport[] })),
        reportsApi.statusWise(),
        reportsApi.sourceWise(),
        reportsApi.dateWise(startDate, endDate).catch(() => null),
      ]);
      setUserData(userRes.data);
      setStatusData(statusRes.data);
      setSourceData(sourceRes.data);
      setDateData(dateRes?.data ?? null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchReports(); }, []);

  const STATUS_COLORS: Record<string, string> = {
    NEW: '#3B82F6', CONTACTED: '#F59E0B', DEMO: '#8B5CF6',
    NEGOTIATION: '#F97316', WON: '#16A34A', LOST: '#DC2626',
  };

  const handleCsvExport = (type: string, hasParams = false) => {
    const base = '/api/reports';
    window.open(hasParams ? `${base}/${type}&export=csv` : `${base}/${type}/?export=csv`, '_blank');
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2"><BarChart3 size={18} className="text-blue-600" /><h3 className="font-semibold text-gray-900">Leads by Status</h3></div>
              <Button variant="ghost" size="sm" onClick={() => handleCsvExport('status-wise')}><Download size={14} /> CSV</Button>
            </div>
          </CardHeader>
          <CardBody>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={statusData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {statusData.map((entry) => <Cell key={entry.status} fill={STATUS_COLORS[entry.status] || '#999'} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2"><Globe size={18} className="text-cyan-600" /><h3 className="font-semibold text-gray-900">Leads by Source</h3></div>
              <Button variant="ghost" size="sm" onClick={() => handleCsvExport('source-wise')}><Download size={14} /> CSV</Button>
            </div>
          </CardHeader>
          <CardBody>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={sourceData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis type="number" tick={{ fontSize: 12 }} />
                <YAxis dataKey="source_name" type="category" tick={{ fontSize: 12 }} width={100} />
                <Tooltip />
                <Bar dataKey="count" fill="#2563EB" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>
      </div>

      {(isAdmin || isManager) && (
        <>
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2"><Users size={18} className="text-purple-600" /><h3 className="font-semibold text-gray-900">User Performance</h3></div>
                <Button variant="ghost" size="sm" onClick={() => handleCsvExport('user-wise')}><Download size={14} /> CSV</Button>
              </div>
            </CardHeader>
            <CardBody>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {['User', 'Total Leads', 'Won', 'Lost', 'Customers', 'Pending Follow-ups'].map((h) => <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase">{h}</th>)}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {userData.map((u) => (
                      <tr key={u.user_id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">{u.user_name}</td>
                        <td className="px-4 py-3 text-sm">{u.total_leads}</td>
                        <td className="px-4 py-3 text-sm text-green-600 font-medium">{u.won_leads}</td>
                        <td className="px-4 py-3 text-sm text-red-600">{u.lost_leads}</td>
                        <td className="px-4 py-3 text-sm">{u.customers}</td>
                        <td className="px-4 py-3 text-sm">{u.pending_followups}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2"><Calendar size={18} className="text-orange-600" /><h3 className="font-semibold text-gray-900">Date Range Report</h3></div>
                <Button variant="ghost" size="sm" onClick={() => handleCsvExport(`date-wise?start=${startDate}&end=${endDate}`, true)}><Download size={14} /> CSV</Button>
              </div>
            </CardHeader>
            <CardBody>
              <div className="flex gap-3 mb-4">
                <div><label className="block text-xs text-gray-500 mb-1">Start</label><input type="date" className="input-field" value={startDate} onChange={(e) => setStartDate(e.target.value)} /></div>
                <div><label className="block text-xs text-gray-500 mb-1">End</label><input type="date" className="input-field" value={endDate} onChange={(e) => setEndDate(e.target.value)} /></div>
                <div className="self-end"><Button size="sm" onClick={fetchReports}>Apply</Button></div>
              </div>
              {dateData && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  {[
                    { label: 'Leads Created', value: dateData.leads_created, color: 'text-blue-600' },
                    { label: 'Customers Converted', value: dateData.customers_converted, color: 'text-green-600' },
                    { label: 'Follow-ups Created', value: dateData.followups_created, color: 'text-amber-600' },
                    { label: 'Pipeline Value', value: `$${dateData.pipeline_value.toLocaleString()}`, color: 'text-purple-600' },
                  ].map((s) => (
                    <div key={s.label} className="p-4 rounded-xl bg-gray-50">
                      <p className="text-xs text-gray-500">{s.label}</p>
                      <p className={`text-xl font-bold mt-1 ${s.color}`}>{s.value}</p>
                    </div>
                  ))}
                </div>
              )}
            </CardBody>
          </Card>
        </>
      )}
    </div>
  );
}
