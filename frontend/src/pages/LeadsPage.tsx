import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, Download, RefreshCw, Filter, MoreHorizontal, Edit, Trash2, Repeat } from 'lucide-react';
import { Card, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge, StatusBadge, PriorityBadge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { DataTable, type Column } from '../components/ui/DataTable';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { leadsApi, leadSourcesApi } from '../api/leads';
import type { Lead, LeadSource } from '../types';
import { useAuth } from '../contexts/AuthContext';

export function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [sources, setSources] = useState<LeadSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [showFilters, setShowFilters] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [showEdit, setShowEdit] = useState<Lead | null>(null);
  const [convertId, setConvertId] = useState<string | null>(null);
  const [formData, setFormData] = useState<Partial<Lead>>({});
  const { user, isExecutive, isAdmin, isManager } = useAuth();
  const navigate = useNavigate();

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (search) params.search = search;
      Object.entries(filters).forEach(([k, v]) => { if (v) params[k] = v; });
      const [leadRes, srcRes] = await Promise.all([
        leadsApi.list(params),
        leadSourcesApi.list(),
      ]);
      setLeads(leadRes.data);
      setSources(srcRes.data);
    } finally {
      setLoading(false);
    }
  }, [search, filters]);

  useEffect(() => { fetch(); }, [fetch]);

  const handleCreate = async () => {
    await leadsApi.create(formData);
    setShowCreate(false);
    setFormData({});
    fetch();
  };

  const handleUpdate = async () => {
    if (!showEdit) return;
    const payload = { ...formData };
    if (isExecutive) {
      delete payload.assigned_to;
      delete payload.created_by;
    }
    await leadsApi.update(showEdit.id, payload);
    setShowEdit(null);
    setFormData({});
    fetch();
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this lead?')) return;
    await leadsApi.delete(id);
    fetch();
  };

  const handleConvert = async (id: string) => {
    try {
      await leadsApi.convert(id);
      setConvertId(null);
      fetch();
    } catch {
      alert('Conversion failed. Lead must be WON and not already converted.');
    }
  };

  const openEdit = (lead: Lead) => {
    setShowEdit(lead);
    setFormData(lead);
  };

  const columns: Column<Lead>[] = [
    { key: 'first_name', header: 'Name', sortable: true, render: (r) => `${r.first_name} ${r.last_name}` },
    { key: 'company', header: 'Company', sortable: true },
    { key: 'phone', header: 'Phone' },
    { key: 'email', header: 'Email' },
    { key: 'source_name', header: 'Source' },
    { key: 'status', header: 'Status', render: (r) => <StatusBadge status={r.status} /> },
    { key: 'priority', header: 'Priority', render: (r) => <PriorityBadge priority={r.priority} /> },
    { key: 'estimated_value', header: 'Value', sortable: true, render: (r) => `$${parseFloat(r.estimated_value).toLocaleString()}` },
    { key: 'assigned_to_name', header: 'Assigned To', render: (r) => r.assigned_to_name || '—' },
    { key: 'created_at', header: 'Created', sortable: true, render: (r) => new Date(r.created_at).toLocaleDateString() },
    {
      key: 'actions', header: '', className: 'w-20',
      render: (r) => (
        <div className="flex items-center gap-1">
          <button onClick={(e) => { e.stopPropagation(); openEdit(r); }} className="p-1.5 text-gray-400 hover:text-blue-600 rounded-lg hover:bg-blue-50"><Edit size={15} /></button>
          <button onClick={(e) => { e.stopPropagation(); setConvertId(r.id); }} className="p-1.5 text-gray-400 hover:text-green-600 rounded-lg hover:bg-green-50"><Repeat size={15} /></button>
          {(isAdmin || isManager) && (
            <button onClick={(e) => { e.stopPropagation(); handleDelete(r.id); }} className="p-1.5 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50"><Trash2 size={15} /></button>
          )}
        </div>
      ),
    },
  ];

  const formFields = (lead?: Lead) => (
    <div className="grid grid-cols-2 gap-4">
      <div><label className="block text-sm font-medium text-gray-700 mb-1">First Name</label><input className="input-field" value={formData.first_name || ''} onChange={(e) => setFormData({ ...formData, first_name: e.target.value })} /></div>
      <div><label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label><input className="input-field" value={formData.last_name || ''} onChange={(e) => setFormData({ ...formData, last_name: e.target.value })} /></div>
      <div><label className="block text-sm font-medium text-gray-700 mb-1">Email</label><input className="input-field" value={formData.email || ''} onChange={(e) => setFormData({ ...formData, email: e.target.value })} /></div>
      <div><label className="block text-sm font-medium text-gray-700 mb-1">Phone</label><input className="input-field" value={formData.phone || ''} onChange={(e) => setFormData({ ...formData, phone: e.target.value })} /></div>
      <div><label className="block text-sm font-medium text-gray-700 mb-1">Company</label><input className="input-field" value={formData.company || ''} onChange={(e) => setFormData({ ...formData, company: e.target.value })} /></div>
      <div><label className="block text-sm font-medium text-gray-700 mb-1">Job Title</label><input className="input-field" value={formData.job_title || ''} onChange={(e) => setFormData({ ...formData, job_title: e.target.value })} /></div>
      <div><label className="block text-sm font-medium text-gray-700 mb-1">Source</label>
        <select className="input-field" value={formData.source || ''} onChange={(e) => setFormData({ ...formData, source: e.target.value })}>
          <option value="">Select</option>
          {sources.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
      </div>
      <div><label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
        <select className="input-field" value={formData.status || ''} onChange={(e) => setFormData({ ...formData, status: e.target.value as Lead['status'] })}>
          {['NEW', 'CONTACTED', 'DEMO', 'NEGOTIATION', 'WON', 'LOST'].map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>
      <div><label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
        <select className="input-field" value={formData.priority || ''} onChange={(e) => setFormData({ ...formData, priority: e.target.value as Lead['priority'] })}>
          {['LOW', 'MEDIUM', 'HIGH', 'URGENT'].map((p) => <option key={p} value={p}>{p}</option>)}
        </select>
      </div>
      <div><label className="block text-sm font-medium text-gray-700 mb-1">Estimated Value ($)</label><input type="number" className="input-field" value={formData.estimated_value || ''} onChange={(e) => setFormData({ ...formData, estimated_value: e.target.value })} /></div>
      {!isExecutive && (
        <div className="col-span-2"><label className="block text-sm font-medium text-gray-700 mb-1">Assigned To (User ID)</label><input className="input-field" value={formData.assigned_to || ''} onChange={(e) => setFormData({ ...formData, assigned_to: e.target.value })} placeholder="UUID of user" /></div>
      )}
    </div>
  );

  return (
    <div>
      <Card>
        <CardBody>
          <div className="flex flex-wrap items-center gap-3 mb-4">
            <div className="flex items-center gap-2 bg-gray-100 rounded-xl px-3.5 py-2 text-sm flex-1 min-w-[200px]">
              <Search size={16} className="text-gray-400" />
              <input type="text" placeholder="Search leads..." className="bg-transparent border-none outline-none text-gray-700 w-full" value={search} onChange={(e) => setSearch(e.target.value)} />
            </div>
            <Button variant="secondary" size="sm" onClick={() => setShowFilters(!showFilters)}><Filter size={16} /> Filters</Button>
            <Button variant="secondary" size="sm" onClick={fetch}><RefreshCw size={16} /> Refresh</Button>
            <Button size="sm" onClick={() => { setFormData({}); setShowCreate(true); }}><Plus size={16} /> Add Lead</Button>
          </div>

          {showFilters && (
            <div className="flex flex-wrap gap-3 mb-4 p-4 bg-gray-50 rounded-xl">
              <select className="input-field w-auto" value={filters.status || ''} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
                <option value="">All Status</option>
                {['NEW', 'CONTACTED', 'DEMO', 'NEGOTIATION', 'WON', 'LOST'].map((s) => <option key={s}>{s}</option>)}
              </select>
              <select className="input-field w-auto" value={filters.priority || ''} onChange={(e) => setFilters({ ...filters, priority: e.target.value })}>
                <option value="">All Priority</option>
                {['LOW', 'MEDIUM', 'HIGH', 'URGENT'].map((p) => <option key={p}>{p}</option>)}
              </select>
              {(filters.status || filters.priority) && (
                <Button variant="ghost" size="sm" onClick={() => setFilters({})}>Clear</Button>
              )}
            </div>
          )}

          <DataTable columns={columns} data={leads} keyExtractor={(r) => r.id} onRowClick={(r) => navigate(`/leads/${r.id}`)} loading={loading} emptyMessage="No leads found. Create your first lead!" />
        </CardBody>
      </Card>

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Create Lead" size="lg">
        {formFields()}
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="secondary" onClick={() => setShowCreate(false)}>Cancel</Button>
          <Button onClick={handleCreate}>Create Lead</Button>
        </div>
      </Modal>

      <Modal open={!!showEdit} onClose={() => setShowEdit(null)} title="Edit Lead" size="lg">
        {formFields(showEdit!)}
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="secondary" onClick={() => setShowEdit(null)}>Cancel</Button>
          <Button onClick={handleUpdate}>Save Changes</Button>
        </div>
      </Modal>

      <Modal open={!!convertId} onClose={() => setConvertId(null)} title="Convert Lead" size="sm">
        <p className="text-gray-600 mb-4">Convert this lead to a customer? The lead must have WON status.</p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setConvertId(null)}>Cancel</Button>
          <Button variant="success" onClick={() => handleConvert(convertId!)}>Convert to Customer</Button>
        </div>
      </Modal>
    </div>
  );
}
