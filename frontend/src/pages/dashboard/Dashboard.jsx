import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import DashboardShell from "@/components/DashboardShell";

export default function Dashboard() {
  const { user } = useAuth();
  const [scores, setScores] = useState([]);
  const [draws, setDraws] = useState([]);
  const [winnings, setWinnings] = useState([]);
  const [charity, setCharity] = useState(null);

  useEffect(() => {
    api.get("/scores").then((r) => setScores(r.data)).catch(() => {});
    api.get("/draws/mine/participation").then((r) => setDraws(r.data)).catch(() => {});
    api.get("/winners/mine").then((r) => setWinnings(r.data)).catch(() => {});
    if (user?.charity_id) {
      api.get(`/charities/${user.charity_id}`).then((r) => setCharity(r.data)).catch(() => {});
    }
  }, [user]);

  const isActive = user?.subscription_status === "active";

  return (
    <DashboardShell>
      <div data-testid="dashboard-overview">
        <div className="overline mb-3">Welcome back</div>
        <h1 className="font-heading text-4xl font-semibold tracking-tight mb-2">{user?.name?.split(" ")[0]}.</h1>
        <p className="text-[#5C5A56] mb-10">Your impact, scores, and draw history — at a glance.</p>

        {!isActive && (
          <div className="card-surface p-6 mb-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-[#FFF4E9]" data-testid="dashboard-inactive-banner">
            <div>
              <div className="font-heading text-lg font-medium">Activate your subscription</div>
              <p className="text-sm text-[#5C5A56]">You need an active subscription to participate in the monthly draw.</p>
            </div>
            <Link to="/pricing" className="btn-primary">Choose plan</Link>
          </div>
        )}

        <div className="grid sm:grid-cols-3 gap-5 mb-10">
          <div className="card-surface p-6" data-testid="card-subscription">
            <div className="overline mb-2">Subscription</div>
            <div className="font-heading text-2xl font-medium capitalize">{user?.subscription_plan || "None"}</div>
            <div className={`text-sm mt-1 ${isActive ? "text-[#5B7B5A]" : "text-[#8E8D8A]"}`}>{user?.subscription_status}</div>
            {user?.subscription_end && <div className="text-xs text-[#8E8D8A] mt-2">Renews / ends: {new Date(user.subscription_end).toLocaleDateString()}</div>}
          </div>
          <div className="card-surface p-6" data-testid="card-charity">
            <div className="overline mb-2">Your charity</div>
            <div className="font-heading text-lg font-medium">{charity?.name || "Not selected"}</div>
            <div className="text-sm text-[#5C5A56] mt-1">{user?.charity_percentage}% of your subscription</div>
          </div>
          <div className="card-surface p-6" data-testid="card-participation">
            <div className="overline mb-2">Participation</div>
            <div className="font-heading text-2xl font-medium">{draws.length}</div>
            <div className="text-sm text-[#5C5A56] mt-1">draws tracked</div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <section className="card-surface p-8" data-testid="section-recent-scores">
            <div className="flex items-center justify-between mb-5">
              <h2 className="font-heading text-xl font-medium">Recent scores</h2>
              <Link to="/dashboard/scores" className="text-[#1E3A2F] text-sm font-medium">Manage →</Link>
            </div>
            {scores.length === 0 ? (
              <div className="text-[#5C5A56] text-sm">No scores yet. Add your first round.</div>
            ) : (
              <ul className="space-y-2">
                {scores.slice(0, 5).map((s) => (
                  <li key={s.id} className="flex items-center justify-between py-3 border-b border-[#E5E1D8] last:border-0">
                    <div className="text-sm text-[#5C5A56]">{s.date}</div>
                    <div className="font-mono-display text-lg text-[#1C1B1A]">{s.value}</div>
                  </li>
                ))}
              </ul>
            )}
          </section>
          <section className="card-surface p-8" data-testid="section-winnings">
            <div className="flex items-center justify-between mb-5">
              <h2 className="font-heading text-xl font-medium">Winnings</h2>
              <Link to="/dashboard/winnings" className="text-[#1E3A2F] text-sm font-medium">View all →</Link>
            </div>
            {winnings.length === 0 ? (
              <div className="text-[#5C5A56] text-sm">No wins yet. Keep playing!</div>
            ) : (
              <ul className="space-y-2">
                {winnings.slice(0, 5).map((w) => (
                  <li key={w.id} className="flex items-center justify-between py-3 border-b border-[#E5E1D8] last:border-0">
                    <div>
                      <div className="text-sm font-medium">{w.tier}</div>
                      <div className="text-xs text-[#8E8D8A]">{w.month}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-mono-display text-[#D95D39]">${w.prize_amount}</div>
                      <div className="text-xs text-[#8E8D8A]">{w.payout_status}</div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </div>
    </DashboardShell>
  );
}
