import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import DashboardShell from "@/components/DashboardShell";

export default function AdminDashboard() {
  const [s, setS] = useState(null);
  useEffect(() => { api.get("/admin/reports/summary").then((r) => setS(r.data)); }, []);

  return (
    <DashboardShell admin>
      <div data-testid="admin-overview">
        <h1 className="font-heading text-4xl font-semibold tracking-tight mb-2">Admin overview</h1>
        <p className="text-[#5C5A56] mb-10">Live platform stats.</p>
        {!s ? <div>Loading...</div> : (
          <div className="grid sm:grid-cols-3 gap-4">
            {[
              { l: "Users", v: s.total_users },
              { l: "Active Subscribers", v: s.active_subscribers },
              { l: "Charities", v: s.total_charities },
              { l: "Winners", v: s.total_winners },
              { l: "Pending payouts", v: s.pending_payouts },
              { l: "Total revenue (USD)", v: `$${s.total_revenue}` },
              { l: "Charity estimate (USD)", v: `$${s.charity_contribution_estimate}` },
              { l: "Current prize pool", v: `$${s.current_prize_pool}` },
            ].map((x, i) => (
              <div key={i} className="card-surface p-6" data-testid={`admin-stat-${i}`}>
                <div className="overline mb-2">{x.l}</div>
                <div className="font-heading text-3xl font-semibold">{x.v}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardShell>
  );
}
