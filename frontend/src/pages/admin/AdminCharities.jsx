import { useEffect, useState } from "react";
import { api, formatApiErrorDetail } from "@/lib/api";
import DashboardShell from "@/components/DashboardShell";
import { toast } from "sonner";
import { Trash2 } from "lucide-react";

const EMPTY = { name: "", short_description: "", description: "", image_url: "", category: "General", featured: false };

export default function AdminCharities() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const load = () => api.get("/charities").then((r) => setItems(r.data));
  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    try {
      await api.post("/charities", form);
      setForm(EMPTY);
      toast.success("Charity added");
      load();
    } catch (e2) {
      toast.error(formatApiErrorDetail(e2.response?.data?.detail) || "Error");
    }
  };
  const del = async (id) => {
    if (!window.confirm("Delete this charity?")) return;
    await api.delete(`/charities/${id}`);
    load();
  };
  const toggleFeatured = async (c) => {
    await api.patch(`/charities/${c.id}`, { featured: !c.featured });
    load();
  };

  return (
    <DashboardShell admin>
      <div data-testid="admin-charities">
        <h1 className="font-heading text-4xl font-semibold tracking-tight mb-6">Charities</h1>

        <form onSubmit={submit} className="card-surface p-8 mb-6 grid sm:grid-cols-2 gap-3" data-testid="admin-charity-form">
          <input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required className="bg-white border border-[#E5E1D8] rounded-xl px-4 py-3" data-testid="admin-charity-name" />
          <input placeholder="Category" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} className="bg-white border border-[#E5E1D8] rounded-xl px-4 py-3" />
          <input placeholder="Short description" value={form.short_description} onChange={(e) => setForm({ ...form, short_description: e.target.value })} required className="bg-white border border-[#E5E1D8] rounded-xl px-4 py-3 sm:col-span-2" />
          <textarea placeholder="Full description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required className="bg-white border border-[#E5E1D8] rounded-xl px-4 py-3 sm:col-span-2" rows={3} />
          <input placeholder="Image URL" value={form.image_url} onChange={(e) => setForm({ ...form, image_url: e.target.value })} required className="bg-white border border-[#E5E1D8] rounded-xl px-4 py-3 sm:col-span-2" />
          <button className="btn-primary sm:col-span-2" data-testid="admin-charity-submit">Add charity</button>
        </form>

        <div className="grid md:grid-cols-2 gap-4">
          {items.map((c) => (
            <div key={c.id} className="card-surface p-5 flex gap-4" data-testid={`admin-charity-${c.id}`}>
              <img src={c.image_url} alt="" className="w-20 h-20 object-cover rounded-lg flex-shrink-0" />
              <div className="flex-1">
                <div className="font-medium">{c.name} {c.featured && <span className="text-xs bg-[#D95D39] text-white px-2 py-0.5 rounded-full ml-1">Featured</span>}</div>
                <div className="text-xs text-[#8E8D8A]">{c.category}</div>
                <div className="text-sm text-[#5C5A56] line-clamp-2 mt-1">{c.short_description}</div>
                <div className="flex gap-3 mt-3 text-xs">
                  <button onClick={() => toggleFeatured(c)} className="text-[#1E3A2F] font-medium" data-testid={`admin-feature-${c.id}`}>{c.featured ? "Unfeature" : "Feature"}</button>
                  <button onClick={() => del(c.id)} className="text-red-600 flex items-center gap-1" data-testid={`admin-delete-${c.id}`}><Trash2 size={14} /> Delete</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </DashboardShell>
  );
}
