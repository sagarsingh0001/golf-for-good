import { useEffect, useState } from "react";
import { api, formatApiErrorDetail } from "@/lib/api";
import DashboardShell from "@/components/DashboardShell";
import { toast } from "sonner";

export default function AdminDraws() {
  const [draws, setDraws] = useState([]);
  const [month, setMonth] = useState("");
  const [logic, setLogic] = useState("random");
  const [preview, setPreview] = useState(null);

  const load = () => api.get("/draws/admin/all").then((r) => setDraws(r.data));
  useEffect(() => { load(); }, []);

  const configure = async () => {
    try {
      await api.post("/draws/configure", { month, logic_type: logic });
      toast.success("Draft saved");
      load();
    } catch (e) {
      toast.error(formatApiErrorDetail(e.response?.data?.detail) || "Error");
    }
  };
  const simulate = async () => {
    try {
      const { data } = await api.post("/draws/simulate", { month, logic_type: logic });
      setPreview(data);
    } catch (e) {
      toast.error(formatApiErrorDetail(e.response?.data?.detail) || "Error");
    }
  };
  const publish = async (d) => {
    if (!window.confirm(`Publish draw for ${d.month}? Winners will be notified.`)) return;
    try {
      const { data } = await api.post("/draws/publish", { draw_id: d.id });
      toast.success(`Published. Winners: ${data.winners_count}. Rollover: $${data.rollover}`);
      load();
    } catch (e) {
      toast.error(formatApiErrorDetail(e.response?.data?.detail) || "Error");
    }
  };

  return (
    <DashboardShell admin>
      <div data-testid="admin-draws">
        <h1 className="font-heading text-4xl font-semibold tracking-tight mb-6">Draws</h1>

        <div className="card-surface p-8 mb-6">
          <h2 className="font-heading text-xl font-medium mb-4">Configure / simulate a draw</h2>
          <div className="grid sm:grid-cols-3 gap-3 mb-4">
            <input type="month" value={month} onChange={(e) => setMonth(e.target.value)} className="bg-white border border-[#E5E1D8] rounded-xl px-4 py-3" data-testid="admin-draw-month" />
            <select value={logic} onChange={(e) => setLogic(e.target.value)} className="bg-white border border-[#E5E1D8] rounded-xl px-4 py-3" data-testid="admin-draw-logic">
              <option value="random">Random</option>
              <option value="algorithmic">Algorithmic (score-weighted)</option>
            </select>
          </div>
          <div className="flex gap-3">
            <button onClick={simulate} className="btn-outline" data-testid="admin-draw-simulate">Simulate</button>
            <button onClick={configure} className="btn-secondary" data-testid="admin-draw-configure">Save draft</button>
          </div>
          {preview && (
            <div className="mt-6 p-5 bg-[#F0EFEA] rounded-xl" data-testid="admin-draw-preview">
              <div className="overline mb-2">Simulation preview</div>
              <div className="flex gap-2 mb-3">{preview.numbers.map((n) => <span key={n} className="w-10 h-10 bg-white border border-[#E5E1D8] rounded-full flex items-center justify-center font-mono-display">{n}</span>)}</div>
              <div className="text-sm text-[#5C5A56]">
                Active users: {preview.active_users} · Pool: ${preview.prize_pool.total_pool} · 5-match: {preview.projected_winners.tier_5} · 4-match: {preview.projected_winners.tier_4} · 3-match: {preview.projected_winners.tier_3}
              </div>
            </div>
          )}
        </div>

        <div className="card-surface p-8">
          <h2 className="font-heading text-xl font-medium mb-4">All draws</h2>
          {draws.length === 0 ? <div className="text-[#5C5A56] text-sm">None yet.</div> : (
            <ul className="space-y-3">
              {draws.map((d) => (
                <li key={d.id} className="flex items-center justify-between border-b border-[#E5E1D8] py-3" data-testid={`admin-draw-${d.month}`}>
                  <div>
                    <div className="font-medium">{d.month} <span className="text-xs text-[#8E8D8A] ml-2">{d.logic_type} · {d.status}</span></div>
                    <div className="flex gap-1 mt-2">{d.numbers.map((n) => <span key={n} className="w-8 h-8 bg-[#EBE6DD] rounded-full flex items-center justify-center font-mono-display text-xs">{n}</span>)}</div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-xs text-[#5C5A56]">Pool: ${d.prize_pool?.total_pool || 0}</div>
                    {d.status === "draft" && <button onClick={() => publish(d)} className="btn-primary !py-2 !px-4 text-sm" data-testid={`admin-publish-${d.id}`}>Publish</button>}
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
