import { useEffect, useState } from "react";
import { api, formatApiErrorDetail, API } from "@/lib/api";
import DashboardShell from "@/components/DashboardShell";
import { toast } from "sonner";

export default function AdminWinners() {
  const [rows, setRows] = useState([]);
  const load = () => api.get("/winners/admin/all").then((r) => setRows(r.data));
  useEffect(() => { load(); }, []);

  const verify = async (id, action) => {
    try {
      await api.post("/winners/verify", { winner_id: id, action });
      toast.success(`Marked ${action}`);
      load();
    } catch (e) { toast.error(formatApiErrorDetail(e.response?.data?.detail) || "Error"); }
  };
  const pay = async (id) => {
    await api.post("/winners/payout", { winner_id: id, payout_status: "paid" });
    toast.success("Marked paid");
    load();
  };

  return (
    <DashboardShell admin>
      <div data-testid="admin-winners">
        <h1 className="font-heading text-4xl font-semibold tracking-tight mb-6">Winners</h1>
        {rows.length === 0 ? <div className="card-surface p-10 text-[#5C5A56] text-center">No winners yet.</div> : (
          <div className="space-y-3">
            {rows.map((w) => (
              <div key={w.id} className="card-surface p-6 grid md:grid-cols-5 gap-4 items-center" data-testid={`admin-winner-${w.id}`}>
                <div>
                  <div className="font-medium">{w.name}</div>
                  <div className="text-xs text-[#8E8D8A]">{w.email}</div>
                </div>
                <div>
                  <div className="overline !text-[#5C5A56] mb-1">{w.month}</div>
                  <div className="text-sm">{w.tier}</div>
                </div>
                <div className="font-mono-display text-[#D95D39]">${w.prize_amount}</div>
                <div className="flex flex-col gap-1 text-xs">
                  <span>Verify: <strong className="capitalize">{w.verification_status}</strong></span>
                  <span>Payout: <strong className="capitalize">{w.payout_status}</strong></span>
                </div>
                <div className="flex flex-wrap gap-2 text-xs">
                  {w.proof_storage_path && (
                    <a href={`${API}/files/view?path=${encodeURIComponent(w.proof_storage_path)}`} target="_blank" rel="noopener noreferrer" className="text-[#1E3A2F] underline" data-testid={`admin-winner-proof-${w.id}`}>View proof</a>
                  )}
                  {w.verification_status === "pending" && (
                    <>
                      <button onClick={() => verify(w.id, "approve")} className="bg-[#5B7B5A] text-white px-3 py-1 rounded-full" data-testid={`admin-winner-approve-${w.id}`}>Approve</button>
                      <button onClick={() => verify(w.id, "reject")} className="bg-red-500 text-white px-3 py-1 rounded-full">Reject</button>
                    </>
                  )}
                  {w.verification_status === "approved" && w.payout_status === "pending" && (
                    <button onClick={() => pay(w.id)} className="bg-[#D95D39] text-white px-3 py-1 rounded-full" data-testid={`admin-winner-pay-${w.id}`}>Mark paid</button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardShell>
  );
}
