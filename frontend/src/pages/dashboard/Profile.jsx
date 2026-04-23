import { useEffect, useState } from "react";
import { api, formatApiErrorDetail } from "@/lib/api";
import DashboardShell from "@/components/DashboardShell";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

export default function ProfilePage() {
  const { user, refresh } = useAuth();
  const [charities, setCharities] = useState([]);
  const [charityId, setCharityId] = useState(user?.charity_id || "");
  const [pct, setPct] = useState(user?.charity_percentage || 10);

  useEffect(() => {
    api.get("/charities").then((r) => setCharities(r.data));
  }, []);

  const save = async () => {
    try {
      await api.patch("/users/me/charity", { charity_id: charityId, charity_percentage: Number(pct) });
      toast.success("Charity preferences updated");
      refresh();
    } catch (e) {
      toast.error(formatApiErrorDetail(e.response?.data?.detail) || "Failed");
    }
  };

  const cancel = async () => {
    if (!window.confirm("Cancel subscription?")) return;
    try {
      await api.post("/subscribe/cancel");
      toast.success("Subscription cancelled");
      refresh();
    } catch (e) {
      toast.error("Cancel failed");
    }
  };

  return (
    <DashboardShell>
      <div data-testid="profile-page">
        <h1 className="font-heading text-4xl font-semibold tracking-tight mb-2">Profile</h1>
        <p className="text-[#5C5A56] mb-10">Manage your charity preferences and subscription.</p>

        <div className="card-surface p-8 mb-6" data-testid="profile-charity-card">
          <h2 className="font-heading text-xl font-medium mb-5">Charity preference</h2>
          <div className="grid sm:grid-cols-2 gap-4 mb-5">
            <div>
              <label className="block text-xs uppercase tracking-wider text-[#5C5A56] mb-1">Charity</label>
              <select value={charityId} onChange={(e) => setCharityId(e.target.value)} className="w-full bg-white border border-[#E5E1D8] rounded-xl px-4 py-3" data-testid="profile-charity-select">
                {charities.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs uppercase tracking-wider text-[#5C5A56] mb-1">Contribution % (10–100)</label>
              <input type="number" min={10} max={100} value={pct} onChange={(e) => setPct(e.target.value)} className="w-full bg-white border border-[#E5E1D8] rounded-xl px-4 py-3" data-testid="profile-pct-input" />
            </div>
          </div>
          <button onClick={save} className="btn-primary" data-testid="profile-save">Save preferences</button>
        </div>

        <div className="card-surface p-8" data-testid="profile-sub-card">
          <h2 className="font-heading text-xl font-medium mb-3">Subscription</h2>
          <div className="text-[#5C5A56] text-sm mb-1">Plan: <strong className="text-[#1C1B1A] capitalize">{user?.subscription_plan || "None"}</strong></div>
          <div className="text-[#5C5A56] text-sm mb-5">Status: <strong className="text-[#1C1B1A] capitalize">{user?.subscription_status}</strong></div>
          {user?.subscription_status === "active" && user?.role !== "admin" && (
            <button onClick={cancel} className="btn-outline" data-testid="profile-cancel-sub">Cancel subscription</button>
          )}
        </div>
      </div>
    </DashboardShell>
  );
}
