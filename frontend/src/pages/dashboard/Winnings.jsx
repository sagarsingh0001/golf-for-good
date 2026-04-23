import { useEffect, useState, useRef } from "react";
import { api, formatApiErrorDetail } from "@/lib/api";
import DashboardShell from "@/components/DashboardShell";
import { toast } from "sonner";
import { Upload } from "lucide-react";

export default function WinningsPage() {
  const [rows, setRows] = useState([]);
  const fileRef = useRef({});

  const load = () => api.get("/winners/mine").then((r) => setRows(r.data));
  useEffect(() => { load(); }, []);

  const upload = async (winnerId, file) => {
    const fd = new FormData();
    fd.append("file", file);
    try {
      await api.post(`/winners/${winnerId}/proof`, fd, { headers: { "Content-Type": "multipart/form-data" } });
      toast.success("Proof uploaded. Awaiting admin verification.");
      load();
    } catch (e) {
      toast.error(formatApiErrorDetail(e.response?.data?.detail) || "Upload failed");
    }
  };

  return (
    <DashboardShell>
      <div data-testid="winnings-page">
        <h1 className="font-heading text-4xl font-semibold tracking-tight mb-2">Winnings</h1>
        <p className="text-[#5C5A56] mb-10">Upload a screenshot of your scorecard to verify wins. Payouts go out after admin approval.</p>

        {rows.length === 0 ? (
          <div className="card-surface p-10 text-center text-[#5C5A56]">No winnings yet. Keep playing!</div>
        ) : (
          <div className="space-y-4">
            {rows.map((w) => (
              <div key={w.id} className="card-surface p-8 grid md:grid-cols-3 gap-6 items-start" data-testid={`winning-${w.id}`}>
                <div>
                  <div className="overline mb-1">{w.month}</div>
                  <div className="font-heading text-xl font-medium">{w.tier}</div>
                </div>
                <div className="font-mono-display text-3xl text-[#D95D39]">${w.prize_amount}</div>
                <div className="flex flex-col gap-3 items-start">
                  <div className="flex gap-3 text-xs">
                    <span className={`px-3 py-1 rounded-full ${w.verification_status === "approved" ? "bg-[#5B7B5A] text-white" : w.verification_status === "rejected" ? "bg-red-500 text-white" : "bg-[#EBE6DD] text-[#5C5A56]"}`}>
                      Verification: {w.verification_status}
                    </span>
                    <span className={`px-3 py-1 rounded-full ${w.payout_status === "paid" ? "bg-[#5B7B5A] text-white" : "bg-[#EBE6DD] text-[#5C5A56]"}`}>
                      Payout: {w.payout_status}
                    </span>
                  </div>
                  {!w.proof_storage_path && w.verification_status !== "approved" && (
                    <>
                      <input
                        type="file"
                        accept="image/*"
                        hidden
                        ref={(el) => (fileRef.current[w.id] = el)}
                        onChange={(e) => e.target.files?.[0] && upload(w.id, e.target.files[0])}
                        data-testid={`winning-file-${w.id}`}
                      />
                      <button onClick={() => fileRef.current[w.id]?.click()} className="btn-outline !py-2 !px-4 text-xs" data-testid={`winning-upload-${w.id}`}>
                        <Upload size={14} /> Upload scorecard proof
                      </button>
                    </>
                  )}
                  {w.proof_storage_path && <div className="text-xs text-[#5C5A56]">✓ Proof submitted</div>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardShell>
  );
}
