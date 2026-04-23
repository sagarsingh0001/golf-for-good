import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { api, formatApiErrorDetail } from "@/lib/api";
import { toast } from "sonner";

export default function Signup() {
  const { register } = useAuth();
  const nav = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", charity_id: "", charity_percentage: 10 });
  const [charities, setCharities] = useState([]);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.get("/charities").then((r) => setCharities(r.data)).catch(() => {});
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    setErr(""); setBusy(true);
    try {
      await register({ ...form, charity_percentage: Number(form.charity_percentage) });
      toast.success("Account created! Pick a plan to activate your subscription.");
      nav("/pricing");
    } catch (e2) {
      setErr(formatApiErrorDetail(e2.response?.data?.detail) || e2.message);
    } finally { setBusy(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F9F8F6] container-px py-16" data-testid="signup-page">
      <div className="card-surface w-full max-w-lg p-10">
        <Link to="/" className="font-heading font-bold text-xl block mb-8">Golf<span className="text-[#D95D39]">.</span>ForGood</Link>
        <h1 className="font-heading text-3xl font-semibold mb-2 tracking-tight">Join a community with purpose.</h1>
        <p className="text-[#5C5A56] mb-8 text-sm">Create your account, pick a charity, and start your subscription.</p>
        <form onSubmit={submit} className="space-y-4" data-testid="signup-form">
          <div>
            <label className="block text-xs uppercase tracking-wider text-[#5C5A56] mb-1">Full name</label>
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required className="w-full bg-white border border-[#E5E1D8] rounded-xl px-4 py-3 focus:outline-none focus:border-[#D95D39]" data-testid="signup-name-input" />
          </div>
          <div>
            <label className="block text-xs uppercase tracking-wider text-[#5C5A56] mb-1">Email</label>
            <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required className="w-full bg-white border border-[#E5E1D8] rounded-xl px-4 py-3 focus:outline-none focus:border-[#D95D39]" data-testid="signup-email-input" />
          </div>
          <div>
            <label className="block text-xs uppercase tracking-wider text-[#5C5A56] mb-1">Password (min 6 chars)</label>
            <input type="password" minLength={6} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required className="w-full bg-white border border-[#E5E1D8] rounded-xl px-4 py-3 focus:outline-none focus:border-[#D95D39]" data-testid="signup-password-input" />
          </div>
          <div>
            <label className="block text-xs uppercase tracking-wider text-[#5C5A56] mb-1">Your charity</label>
            <select value={form.charity_id} onChange={(e) => setForm({ ...form, charity_id: e.target.value })} required className="w-full bg-white border border-[#E5E1D8] rounded-xl px-4 py-3 focus:outline-none focus:border-[#D95D39]" data-testid="signup-charity-select">
              <option value="">Select a charity...</option>
              {charities.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs uppercase tracking-wider text-[#5C5A56] mb-1">Charity contribution % (min 10)</label>
            <input type="number" min={10} max={100} value={form.charity_percentage} onChange={(e) => setForm({ ...form, charity_percentage: e.target.value })} className="w-full bg-white border border-[#E5E1D8] rounded-xl px-4 py-3 focus:outline-none focus:border-[#D95D39]" data-testid="signup-charity-pct" />
          </div>
          {err && <div className="text-sm text-red-600" data-testid="signup-error">{err}</div>}
          <button disabled={busy} className="btn-primary w-full justify-center" data-testid="signup-submit">
            {busy ? "Creating..." : "Create account"}
          </button>
        </form>
        <p className="mt-6 text-sm text-[#5C5A56] text-center">
          Already have one? <Link to="/login" className="text-[#1E3A2F] font-medium">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
