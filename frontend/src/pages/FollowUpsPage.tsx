import { useEffect, useState, useCallback } from 'react';
import { Plus, CheckCircle2 } from 'lucide-react';
import { Card, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { DataTable, type Column } from '../components/ui/DataTable';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { followupsApi } from '../api/followups';
import { leadsApi } from '../api/leads';
import type { FollowUp, Lead } from '../types';
import { useAuth } from '../contexts/AuthContext';

export function FollowUpsPage() {
  const [followups, setFollowups] = useState<FollowUp[]>([]);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [completeId, setCompleteId] = useState<string | null>(null);
  const [outcome, setOutcome] = useState('');
  const [formData, setFormData] = useState<Partial<FollowUp>>({});
  const { user } = useAuth();

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const [fuRes, lRes] = await Promise.all([
        followupsApi.list(),
        leadsApi.list(),
      ]);
      setFollowups(fuRes.data);
      setLeads(lRes.data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetch(); }, [fetch]);

  const handleCreate = async () => {
    await followupsApi.create({ ...formData, assigned_to: formData.assigned_to || user?.id });
    setShowCreate(false);
    setFormData({});
    fetch();
  };

  const handleComplete = async () => {
    if (!completeId) return;
    await followupsApi.complete(completeId, outcome);
    setCompleteId(null);
    setOutcome('');
    fetch();
  };

  const overdue = followups.filter((f) => f.status === 'PENDING' && new Date(f.follow_up_at) < new Date());

  const columns: Column<FollowUp>[] = [
    { key: 'lead', header: 'Lead', render: (r) => {
      const lead = leads.find((l) => l.id === r.lead);
      return lead ? `${lead.first_name} ${lead.last_name}` : r.lead;
    }},
    { key: 'purpose', header: 'Purpose' },
    { key: 'follow_up_at', header: 'Scheduled', sortable: true, render: (r) => new Date(r.follow_up_at).toLocaleString() },
    { key: 'assigned_to_name', header: 'Assigned To' },
    { key: 'status', header: 'Status', render: (r) => (
      <Badge variant={r.status === 'COMPLETED' ? 'success' : r.status === 'CANCELLED' ? 'default' : 'warning'}>{r.status}</Badge>
    )},
    { key: 'actions', header: '', className: 'w-24', render: (r) => (
      r.status === 'PENDING' ? (
        <Button size="sm" variant="success" onClick={(e) => { e.stopPropagation(); setCompleteId(r.id); }}>
          <CheckCircle2 size={14} /> Complete
        </Button>
      ) : null
    )},
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Today\'s', value: followups.filter((f) => new Date(f.follow_up_at).toDateString() === new Date().toDateString()).length, color: 'text-blue-600', bg: 'bg-blue-50' },
          { label: 'Pending', value: followups.filter((f) => f.status === 'PENDING').length, color: 'text-amber-600', bg: 'bg-amber-50' },
          { label: 'Completed', value: followups.filter((f) => f.status === 'COMPLETED').length, color: 'text-green-600', bg: 'bg-green-50' },
          { label: 'Overdue', value: overdue.length, color: 'text-red-600', bg: 'bg-red-50' },
        ].map((stat) => (
          <Card key={stat.label}>
            <CardBody>
              <p className="text-sm text-gray-500">{stat.label}</p>
              <p className={`text-2xl font-bold mt-1 ${stat.color}`}>{stat.value}</p>
            </CardBody>
          </Card>
        ))}
      </div>

      <Card>
        <CardBody>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">All Follow Ups</h2>
            <Button size="sm" onClick={() => setShowCreate(true)}><Plus size={16} /> Schedule Follow Up</Button>
          </div>
          <DataTable
            columns={columns}
            data={followups}
            keyExtractor={(r) => r.id}
            loading={loading}
            emptyMessage="No follow-ups scheduled."
            onRowClick={() => {}}
          />
        </CardBody>
      </Card>

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Schedule Follow Up" size="lg">
        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Lead</label>
            <select className="input-field" value={formData.lead || ''} onChange={(e) => setFormData({ ...formData, lead: e.target.value })}>
              <option value="">Select lead</option>
              {leads.map((l) => <option key={l.id} value={l.id}>{l.first_name} {l.last_name}</option>)}
            </select>
          </div>
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Assigned To</label>
            <p className="text-sm text-gray-700 py-2.5 px-3.5 bg-gray-50 border border-gray-200 rounded-xl">
              {user?.first_name && user?.last_name ? `${user.first_name} ${user.last_name}` : user?.email || '—'}
            </p>
          </div>
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Date & Time</label>
            <input type="datetime-local" className="input-field" value={formData.follow_up_at || ''} onChange={(e) => setFormData({ ...formData, follow_up_at: e.target.value })} />
          </div>
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Purpose</label>
            <textarea className="input-field min-h-[80px]" value={formData.purpose || ''} onChange={(e) => setFormData({ ...formData, purpose: e.target.value })} />
          </div>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="secondary" onClick={() => setShowCreate(false)}>Cancel</Button>
          <Button onClick={handleCreate}>Schedule</Button>
        </div>
      </Modal>

      <Modal open={!!completeId} onClose={() => setCompleteId(null)} title="Complete Follow Up" size="md">
        <div><label className="block text-sm font-medium text-gray-700 mb-1">Outcome</label>
          <textarea className="input-field min-h-[80px]" value={outcome} onChange={(e) => setOutcome(e.target.value)} placeholder="Describe the outcome..." />
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="secondary" onClick={() => setCompleteId(null)}>Cancel</Button>
          <Button variant="success" onClick={handleComplete}>Mark Completed</Button>
        </div>
      </Modal>
    </div>
  );
}
