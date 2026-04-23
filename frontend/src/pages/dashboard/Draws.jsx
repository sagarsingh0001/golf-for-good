import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import DashboardShell from "@/components/DashboardShell";

export default function DrawsPage() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    api.get("/draws/mine/participation").then((r) => setRows(r.data));
  }, []);

  return (
    <DashboardShell>
      <div data-testid="draws-page">
        <h1 className="font-heading text-4xl font-semibold tracking-tight mb-2">Monthly draws</h1>
        <p className="text-[#5C5A56] mb-10">Compare your latest 5 scores with the winning numbers each month.</p>

        {rows.length === 0 ? (
          <div className="card-surface p-10 text-center text-[#5C5A56]">No published draws yet.</div>
        ) : (
          <div className="space-y-4">
            {rows.map((r) => (
              <div key={r.month} className="card-surface p-8" data-testid={`draw-row-${r.month}`}>
                <div className="flex items-center justify-between mb-5">
                  <div>
                    <div className="overline mb-1">{r.month}</div>
                    <div className="font-heading text-xl font-medium">{r.matches} / 5 matches</div>
                  </div>
                  <div className={`px-4 py-1.5 rounded-full text-xs font-semibold ${r.matches >= 3 ? "bg-[#D95D39] text-white" : "bg-[#EBE6DD] text-[#5C5A56]"}`}>
                    {r.matches >= 5 ? "JACKPOT" : r.matches === 4 ? "4-match win" : r.matches === 3 ? "3-match win" : "No win"}
                  </div>
                </div>
                <div className="grid sm:grid-cols-2 gap-6">
                  <div>
                    <div className="text-xs uppercase tracking-wider text-[#8E8D8A] mb-2">Winning numbers</div>
                    <div className="flex gap-2 flex-wrap">
                      {r.numbers.map((n) => (
                        <span key={n} className={`w-11 h-11 rounded-full flex items-center justify-center font-mono-display ${r.your_numbers.includes(n) ? "bg-[#D95D39] text-white" : "bg-[#EBE6DD] text-[#1C1B1A]"}`}>
                          {n}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs uppercase tracking-wider text-[#8E8D8A] mb-2">Your numbers</div>
                    <div className="flex gap-2 flex-wrap">
                      {r.your_numbers.length === 0 ? <span className="text-[#8E8D8A] text-sm">Enter 5 scores to participate.</span> : r.your_numbers.map((n, idx) => (
                        <span key={idx} className={`w-11 h-11 rounded-full flex items-center justify-center font-mono-display border ${r.numbers.includes(n) ? "border-[#D95D39] text-[#D95D39]" : "border-[#E5E1D8] text-[#1C1B1A]"}`}>{n}</span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardShell>
  );
}
