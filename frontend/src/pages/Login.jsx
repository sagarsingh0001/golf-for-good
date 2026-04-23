import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { formatApiErrorDetail } from "@/lib/api";
import { toast } from "sonner";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setErr(""); setBusy(true);
    try {
      const u = await login(email, password);
      toast.success(`Welcome back, ${u.name}`);
      nav(u.role === "admin" ? "/admin" : "/dashboard");
    } catch (e2) {
      setErr(formatApiErrorDetail(e2.response?.data?.detail) || e2.message);
    } finally { setBusy(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F9F8F6] container-px" data-testid="login-page">
      <div className="card-surface w-full max-w-md p-10">
        <Link to="/" className="font-heading font-bold text-xl block mb-8" data-testid="login-brand">Golf<span className="text-[#D95D39]">.</span>ForGood</Link>
        <h1 className="font-heading text-3xl font-semibold mb-2 tracking-tight">Welcome back.</h1>
        <p className="text-[#5C5A56] mb-8 text-sm">Sign in to manage scores, draws, and your charity.</p>
        <form onSubmit={submit} className="space-y-4" data-testid="login-form">
          <div>
            <label className="block text-xs uppercase tracking-wider text-[#5C5A56] mb-1">Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="w-full bg-white border border-[#E5E1D8] rounded-xl px-4 py-3 focus:outline-none focus:border-[#D95D39]" data-testid="login-email-input" />
          </div>
          <div>
            <label className="block text-xs uppercase tracking-wider text-[#5C5A56] mb-1">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required className="w-full bg-white border border-[#E5E1D8] rounded-xl px-4 py-3 focus:outline-none focus:border-[#D95D39]" data-testid="login-password-input" />
          </div>
          {err && <div className="text-sm text-red-600" data-testid="login-error">{err}</div>}
          <button disabled={busy} className="btn-primary w-full justify-center" data-testid="login-submit">
            {busy ? "Signing in..." : "Sign in"}
          </button>
        </form>
        <p className="mt-6 text-sm text-[#5C5A56] text-center">
          New here? <Link to="/signup" className="text-[#1E3A2F] font-medium" data-testid="login-link-signup">Create an account</Link>
        </p>
      </div>
    </div>
  );
}
