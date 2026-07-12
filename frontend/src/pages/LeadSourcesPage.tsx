import { useEffect, useState, useCallback } from 'react';
import { Plus, Edit, Trash2 } from 'lucide-react';
import { Card, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { leadSourcesApi } from '../api/leads';
import type { LeadSource } from '../types';

export function LeadSourcesPage() {
  const [sources, setSources] = useState<LeadSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [editSource, setEditSource] = useState<LeadSource | null>(null);
  const [formData, setFormData] = useState({ name: '', description: '' });

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const res = await leadSourcesApi.list();
      setSources(res.data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetch(); }, [fetch]);

  const handleCreate = async () => {
    await leadSourcesApi.create(formData);
    setShowCreate(false);
    setFormData({ name: '', description: '' });
    fetch();
  };

  const handleUpdate = async () => {
    if (!editSource) return;
    await leadSourcesApi.update(editSource.id, formData);
    setEditSource(null);
    setFormData({ name: '', description: '' });
    fetch();
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Delete this source?')) return;
    await leadSourcesApi.delete(id);
    fetch();
  };

  return (
    <Card>
      <CardBody>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Lead Sources</h2>
          <Button size="sm" onClick={() => setShowCreate(true)}><Plus size={16} /> Add Source</Button>
        </div>

        {loading ? <LoadingSpinner /> : sources.length === 0 ? (
          <div className="text-center py-12 text-gray-500">No lead sources defined.</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sources.map((source) => (
              <div key={source.id} className="p-5 rounded-xl border border-gray-100 bg-white hover:shadow-sm transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{source.name}</h4>
                  <div className="flex items-center gap-1">
                    <button onClick={() => { setEditSource(source); setFormData({ name: source.name, description: source.description }); }} className="p-1.5 text-gray-400 hover:text-blue-600 rounded-lg"><Edit size={14} /></button>
                    <button onClick={() => handleDelete(source.id)} className="p-1.5 text-gray-400 hover:text-red-600 rounded-lg"><Trash2 size={14} /></button>
                  </div>
                </div>
                {source.description && <p className="text-sm text-gray-500">{source.description}</p>}
                <span className={`badge text-xs mt-2 ${source.is_active ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                  {source.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            ))}
          </div>
        )}
      </CardBody>

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Add Lead Source" size="md">
        <div className="space-y-4">
          <div><label className="block text-sm font-medium text-gray-700 mb-1">Name</label><input className="input-field" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} /></div>
          <div><label className="block text-sm font-medium text-gray-700 mb-1">Description</label><textarea className="input-field" value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} /></div>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="secondary" onClick={() => setShowCreate(false)}>Cancel</Button>
          <Button onClick={handleCreate}>Create</Button>
        </div>
      </Modal>

      <Modal open={!!editSource} onClose={() => setEditSource(null)} title="Edit Lead Source" size="md">
        <div className="space-y-4">
          <div><label className="block text-sm font-medium text-gray-700 mb-1">Name</label><input className="input-field" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} /></div>
          <div><label className="block text-sm font-medium text-gray-700 mb-1">Description</label><textarea className="input-field" value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} /></div>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="secondary" onClick={() => setEditSource(null)}>Cancel</Button>
          <Button onClick={handleUpdate}>Save</Button>
        </div>
      </Modal>
    </Card>
  );
}
