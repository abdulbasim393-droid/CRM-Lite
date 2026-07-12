import { useEffect, useState, useCallback } from 'react';
import { Plus, Edit, Trash2 } from 'lucide-react';
import { Card, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { leadNotesApi, leadsApi } from '../api/leads';
import type { LeadNote, Lead } from '../types';

export function LeadNotesPage() {
  const [notes, setNotes] = useState<LeadNote[]>([]);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [editNote, setEditNote] = useState<LeadNote | null>(null);
  const [formData, setFormData] = useState({ lead: '', note_type: 'CALL', note_text: '' });

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const [nRes, lRes] = await Promise.all([leadNotesApi.list(), leadsApi.list()]);
      setNotes(nRes.data);
      setLeads(lRes.data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetch(); }, [fetch]);

  const handleCreate = async () => {
    await leadNotesApi.create(formData);
    setShowCreate(false);
    setFormData({ lead: '', note_type: 'CALL', note_text: '' });
    fetch();
  };

  const handleUpdate = async () => {
    if (!editNote) return;
    await leadNotesApi.update(editNote.id, formData);
    setEditNote(null);
    setFormData({ lead: '', note_type: 'CALL', note_text: '' });
    fetch();
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Delete this note?')) return;
    await leadNotesApi.delete(id);
    fetch();
  };

  const noteTypeColors: Record<string, string> = {
    CALL: 'bg-blue-50 text-blue-700', WHATSAPP: 'bg-green-50 text-green-700',
    MEETING: 'bg-purple-50 text-purple-700', DEMO: 'bg-amber-50 text-amber-700',
    OBJECTION: 'bg-red-50 text-red-700', OTHER: 'bg-gray-100 text-gray-600',
  };

  return (
    <div>
      <Card>
        <CardBody>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Lead Notes</h2>
            <Button size="sm" onClick={() => setShowCreate(true)}><Plus size={16} /> Add Note</Button>
          </div>

          {loading ? <LoadingSpinner /> : notes.length === 0 ? (
            <div className="text-center py-12 text-gray-500">No notes found.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {notes.map((note) => {
                const lead = leads.find((l) => l.id === note.lead);
                return (
                  <div key={note.id} className="p-5 rounded-xl border border-gray-100 bg-white hover:shadow-sm transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className={`badge text-xs ${noteTypeColors[note.note_type] || 'bg-gray-100 text-gray-600'}`}>{note.note_type}</span>
                        <span className="text-xs text-gray-400">{note.created_by_name}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <button onClick={() => { setEditNote(note); setFormData({ lead: note.lead, note_type: note.note_type, note_text: note.note_text }); }} className="p-1.5 text-gray-400 hover:text-blue-600 rounded-lg"><Edit size={14} /></button>
                        <button onClick={() => handleDelete(note.id)} className="p-1.5 text-gray-400 hover:text-red-600 rounded-lg"><Trash2 size={14} /></button>
                      </div>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{note.note_text}</p>
                    <div className="flex items-center justify-between text-xs text-gray-400">
                      <span>{lead ? `${lead.first_name} ${lead.last_name}` : '—'}</span>
                      <span>{new Date(note.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardBody>
      </Card>

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Add Note" size="md">
        <div className="space-y-4">
          <div><label className="block text-sm font-medium text-gray-700 mb-1">Lead</label>
            <select className="input-field" value={formData.lead} onChange={(e) => setFormData({ ...formData, lead: e.target.value })}>
              <option value="">Select lead</option>
              {leads.map((l) => <option key={l.id} value={l.id}>{l.first_name} {l.last_name}</option>)}
            </select>
          </div>
          <div><label className="block text-sm font-medium text-gray-700 mb-1">Note Type</label>
            <select className="input-field" value={formData.note_type} onChange={(e) => setFormData({ ...formData, note_type: e.target.value })}>
              {['CALL', 'WHATSAPP', 'MEETING', 'DEMO', 'OBJECTION', 'OTHER'].map((t) => <option key={t}>{t}</option>)}
            </select>
          </div>
          <div><label className="block text-sm font-medium text-gray-700 mb-1">Note Text</label>
            <textarea className="input-field min-h-[100px]" value={formData.note_text} onChange={(e) => setFormData({ ...formData, note_text: e.target.value })} />
          </div>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="secondary" onClick={() => setShowCreate(false)}>Cancel</Button>
          <Button onClick={handleCreate}>Add Note</Button>
        </div>
      </Modal>

      <Modal open={!!editNote} onClose={() => setEditNote(null)} title="Edit Note" size="md">
        <div className="space-y-4">
          <div><label className="block text-sm font-medium text-gray-700 mb-1">Note Type</label>
            <select className="input-field" value={formData.note_type} onChange={(e) => setFormData({ ...formData, note_type: e.target.value })}>
              {['CALL', 'WHATSAPP', 'MEETING', 'DEMO', 'OBJECTION', 'OTHER'].map((t) => <option key={t}>{t}</option>)}
            </select>
          </div>
          <div><label className="block text-sm font-medium text-gray-700 mb-1">Note Text</label>
            <textarea className="input-field min-h-[100px]" value={formData.note_text} onChange={(e) => setFormData({ ...formData, note_text: e.target.value })} />
          </div>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="secondary" onClick={() => setEditNote(null)}>Cancel</Button>
          <Button onClick={handleUpdate}>Save</Button>
        </div>
      </Modal>
    </div>
  );
}
