import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Phone, Mail, Globe, Building, User, DollarSign, Calendar, Edit, Plus } from 'lucide-react';
import { Card, CardBody, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { StatusBadge, PriorityBadge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { leadsApi, leadNotesApi } from '../api/leads';
import { followupsApi } from '../api/followups';
import { activityApi } from '../api/activity';
import type { Lead, LeadNote, FollowUp, ActivityLog } from '../types';

export function LeadDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [lead, setLead] = useState<Lead | null>(null);
  const [notes, setNotes] = useState<LeadNote[]>([]);
  const [followups, setFollowups] = useState<FollowUp[]>([]);
  const [activities, setActivities] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<'notes' | 'followups' | 'activity'>('notes');
  const [showNoteModal, setShowNoteModal] = useState(false);
  const [noteForm, setNoteForm] = useState({ note_text: '', note_type: 'CALL' });

  useEffect(() => {
    if (!id) return;
    Promise.all([
      leadsApi.retrieve(id),
      leadNotesApi.list(),
      followupsApi.list(),
      activityApi.list(),
    ]).then(([l, n, f, a]) => {
      setLead(l.data);
      setNotes(n.data.filter((nt: LeadNote) => nt.lead === id));
      setFollowups(f.data.filter((fu: FollowUp) => fu.lead === id));
      setActivities(a.data.filter((act: ActivityLog) => act.entity_id === id || (act.new_value as Record<string, unknown>)?.lead_id === id));
    }).finally(() => setLoading(false));
  }, [id]);

  const handleAddNote = async () => {
    if (!id) return;
    await leadNotesApi.create({ lead: id, ...noteForm });
    setShowNoteModal(false);
    setNoteForm({ note_text: '', note_type: 'CALL' });
    const res = await leadNotesApi.list();
    setNotes(res.data.filter((nt: LeadNote) => nt.lead === id));
  };

  if (loading) return <LoadingSpinner />;
  if (!lead) return <div className="text-center py-12 text-gray-500">Lead not found.</div>;

  return (
    <div className="space-y-6">
      <button onClick={() => navigate('/leads')} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft size={16} /> Back to Leads
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-1">
          <CardHeader>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Lead Information</h2>
              <Button variant="ghost" size="sm"><Edit size={16} /></Button>
            </div>
          </CardHeader>
          <CardBody className="space-y-4">
            <div className="text-center pb-4 border-b border-gray-100">
              <div className="w-16 h-16 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-2xl font-bold mx-auto mb-2">
                {lead.first_name[0]}{lead.last_name[0]}
              </div>
              <h3 className="text-lg font-semibold text-gray-900">{lead.first_name} {lead.last_name}</h3>
              <div className="flex justify-center gap-2 mt-2">
                <StatusBadge status={lead.status} />
                <PriorityBadge priority={lead.priority} />
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-3 text-sm"><Mail size={16} className="text-gray-400" /><span>{lead.email || '—'}</span></div>
              <div className="flex items-center gap-3 text-sm"><Phone size={16} className="text-gray-400" /><span>{lead.phone || '—'}</span></div>
              <div className="flex items-center gap-3 text-sm"><Building size={16} className="text-gray-400" /><span>{lead.company || '—'}</span></div>
              <div className="flex items-center gap-3 text-sm"><Globe size={16} className="text-gray-400" /><span>{lead.website || '—'}</span></div>
              <div className="flex items-center gap-3 text-sm"><User size={16} className="text-gray-400" /><span>{lead.job_title || '—'}</span></div>
              <div className="flex items-center gap-3 text-sm"><DollarSign size={16} className="text-gray-400" /><span>${parseFloat(lead.estimated_value).toLocaleString()}</span></div>
              <div className="flex items-center gap-3 text-sm"><Calendar size={16} className="text-gray-400" /><span>Created {new Date(lead.created_at).toLocaleDateString()}</span></div>
            </div>

            <div className="pt-3 border-t border-gray-100 space-y-1 text-sm">
              <p><span className="text-gray-500">Source:</span> <span className="font-medium">{lead.source_name}</span></p>
              <p><span className="text-gray-500">Assigned To:</span> <span className="font-medium">{lead.assigned_to_name || '—'}</span></p>
            </div>
          </CardBody>
        </Card>

        <div className="lg:col-span-2">
          <Card>
            <div className="border-b border-gray-100">
              <div className="flex">
                {(['notes', 'followups', 'activity'] as const).map((t) => (
                  <button key={t} onClick={() => setTab(t)} className={`px-5 py-3 text-sm font-medium border-b-2 transition-colors ${tab === t ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}>
                    {t === 'notes' ? 'Notes' : t === 'followups' ? 'Follow Ups' : 'Activity'}
                  </button>
                ))}
              </div>
            </div>

            <CardBody>
              {tab === 'notes' && (
                <div className="space-y-4">
                  <div className="flex justify-end">
                    <Button size="sm" onClick={() => setShowNoteModal(true)}><Plus size={16} /> Add Note</Button>
                  </div>
                  {notes.length === 0 ? <p className="text-gray-500 text-sm py-8 text-center">No notes yet.</p> : (
                    notes.map((note) => (
                      <div key={note.id} className="p-4 bg-gray-50 rounded-xl">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="badge bg-blue-50 text-blue-700 text-xs">{note.note_type}</span>
                            <span className="text-xs text-gray-400">{note.created_by_name}</span>
                            <span className="text-xs text-gray-400">{new Date(note.created_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                        <p className="text-sm text-gray-700">{note.note_text}</p>
                      </div>
                    ))
                  )}
                </div>
              )}

              {tab === 'followups' && (
                <div className="space-y-3">
                  {followups.length === 0 ? <p className="text-gray-500 text-sm py-8 text-center">No follow-ups scheduled.</p> : (
                    followups.map((fu) => (
                      <div key={fu.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                        <div>
                          <p className="text-sm font-medium text-gray-900">{fu.purpose}</p>
                          <p className="text-xs text-gray-500 mt-0.5">{new Date(fu.follow_up_at).toLocaleString()} — {fu.assigned_to_name}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`badge text-xs ${fu.status === 'COMPLETED' ? 'bg-green-50 text-green-700' : fu.status === 'CANCELLED' ? 'bg-gray-100 text-gray-600' : 'bg-amber-50 text-amber-700'}`}>
                            {fu.status}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {tab === 'activity' && (
                <div className="space-y-3">
                  {activities.length === 0 ? <p className="text-gray-500 text-sm py-8 text-center">No activity recorded.</p> : (
                    <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-1 before:bottom-1 before:w-0.5 before:bg-gray-200">
                      {activities.map((act) => (
                        <div key={act.id} className="relative">
                          <div className="absolute -left-[18px] top-1 w-3 h-3 rounded-full bg-white border-2 border-blue-500" />
                          <p className="text-sm font-medium text-gray-900">{act.action.replace(/_/g, ' ')} — {act.entity_type.replace(/_/g, ' ')}</p>
                          <p className="text-xs text-gray-400">{act.performed_by_name} · {new Date(act.created_at).toLocaleString()}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </CardBody>
          </Card>
        </div>
      </div>

      <Modal open={showNoteModal} onClose={() => setShowNoteModal(false)} title="Add Note" size="md">
        <div className="space-y-4">
          <div><label className="block text-sm font-medium text-gray-700 mb-1">Note Type</label>
            <select className="input-field" value={noteForm.note_type} onChange={(e) => setNoteForm({ ...noteForm, note_type: e.target.value })}>
              {['CALL', 'WHATSAPP', 'MEETING', 'DEMO', 'OBJECTION', 'OTHER'].map((t) => <option key={t}>{t}</option>)}
            </select>
          </div>
          <div><label className="block text-sm font-medium text-gray-700 mb-1">Note Text</label>
            <textarea className="input-field min-h-[100px]" value={noteForm.note_text} onChange={(e) => setNoteForm({ ...noteForm, note_text: e.target.value })} />
          </div>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <Button variant="secondary" onClick={() => setShowNoteModal(false)}>Cancel</Button>
          <Button onClick={handleAddNote}>Add Note</Button>
        </div>
      </Modal>
    </div>
  );
}
