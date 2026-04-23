import { useEffect, useState } from "react";
import { api, formatApiErrorDetail } from "@/lib/api";
import DashboardShell from "@/components/DashboardShell";
import { toast } from "sonner";
import { Trash2, Edit3, Save, X } from "lucide-react";

export default function ScoresPage() {
  const [scores, setScores] = useState([]);
  const [form, setForm] = useState({ date: "", value: "" });
  const [editingId, setEditingId] = useState(null);
  const [editingVal, setEditingVal] = useState("");

  const load = () => api.get("/scores").then((r) => setScores(r.data)).catch(() => {});
  useEffect(() => { load(); }, []);

  const add = async (e) => {
    e.preventDefault();
    try {
      await api.post("/scores", { date: form.date, value: Number(form.value) });
      setForm({ date: "", value: "" });
      toast.success("Score saved");
      load();
    } catch (e2) {
      toast.error(formatApiErrorDetail(e2.response?.data?.detail) || "Error");
    }
  };

  const del = async (id) => {
    await api.delete(`/scores/${id}`);
    toast.success("Deleted");
    load();
  };

  const saveEdit = async (id) => {
    try {
      await api.patch(`/scores/${id}`, { value: Number(editingVal) });
      setEditingId(null);
      toast.success("Updated");
      load();
    } catch (e) {
      toast.error(formatApiErrorDetail(e.response?.data?.detail) || "Error");
    }
  };

  return (
    <DashboardShell>
      <div data-testid="scores-page">
        <h1 className="font-heading text-4xl font-semibold tracking-tight mb-2">Your scores</h1>
        <p className="text-[#5C5A56] mb-10">The latest 5 Stableford scores count. One per date. New score replaces the oldest.</p>

        <div className="card-surface p-8 mb-8" data-testid="add-score-card">
          <h2 className="font-heading text-xl font-medium mb-5">Add a score</h2>
          <form onSubmit={add} className="grid sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs uppercase tracking-wider text-[#5C5A56] mb-1">Date</label>
              <input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required className="w-full bg-white border border-[#E5E1D8] rounded-xl px-4 py-3" data-testid="score-date-input" />
            </div>
            <div>
              <label className="block text-xs uppercase tracking-wider text-[#5C5A56] mb-1">Score (1-45)</label>
              <input type="number" min={1} max={45} value={form.value} onChange={(e) => setForm({ ...form, value: e.target.value })} required className="w-full bg-white border border-[#E5E1D8] rounded-xl px-4 py-3" data-testid="score-value-input" />
            </div>
            <div className="flex items-end">
              <button className="btn-primary w-full justify-center" data-testid="score-submit">Add score</button>
            </div>
          </form>
        </div>

        <div className="card-surface p-8" data-testid="scores-list-card">
          <h2 className="font-heading text-xl font-medium mb-5">Latest 5 scores</h2>
          {scores.length === 0 ? (
            <div className="text-[#5C5A56] text-sm">No scores yet.</div>
          ) : (
            <ul className="divide-y divide-[#E5E1D8]">
              {scores.map((s) => (
                <li key={s.id} className="flex items-center justify-between py-4" data-testid={`score-row-${s.id}`}>
                  <div>
                    <div className="text-[#1C1B1A] font-medium">{s.date}</div>
                  </div>
                  <div className="flex items-center gap-4">
                    {editingId === s.id ? (
                      <>
                        <input type="number" min={1} max={45} value={editingVal} onChange={(e) => setEditingVal(e.target.value)} className="w-20 bg-white border border-[#E5E1D8] rounded-lg px-3 py-2 text-center" data-testid={`score-edit-input-${s.id}`} />
                        <button onClick={() => saveEdit(s.id)} className="text-[#5B7B5A]" data-testid={`score-save-${s.id}`}><Save size={18} /></button>
                        <button onClick={() => setEditingId(null)} className="text-[#8E8D8A]"><X size={18} /></button>
                      </>
                    ) : (
                      <>
                        <div className="font-mono-display text-2xl text-[#1C1B1A]">{s.value}</div>
                        <button onClick={() => { setEditingId(s.id); setEditingVal(String(s.value)); }} className="text-[#5C5A56] hover:text-[#1C1B1A]" data-testid={`score-edit-${s.id}`}><Edit3 size={16} /></button>
                        <button onClick={() => del(s.id)} className="text-[#5C5A56] hover:text-red-600" data-testid={`score-delete-${s.id}`}><Trash2 size={16} /></button>
                      </>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </DashboardShell>
  );
}
