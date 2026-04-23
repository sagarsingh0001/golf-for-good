import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { api, formatApiErrorDetail } from "@/lib/api";
import { Check } from "lucide-react";
import { toast } from "sonner";

const PLANS = [
  { id: "monthly", name: "Monthly", price: 9.99, cadence: "/month", perks: ["Enter monthly draws", "Your charity contribution — min 10%", "Cancel anytime", "Full access to dashboard"] },
  { id: "yearly", name: "Yearly", price: 99, cadence: "/year", popular: true, perks: ["Everything in Monthly", "2 months free", "Larger annual charity impact", "Priority support"] },
];

export default function Pricing() {
  const { user } = useAuth();
  const nav = useNavigate();
  const [busy, setBusy] = useState(null);

  const subscribe = async (plan) => {
    if (!user) { nav("/signup"); return; }
    setBusy(plan);
    try {
      const { data } = await api.post("/subscribe/checkout", { plan, origin_url: window.location.origin });
      window.location.href = data.url;
    } catch (e) {
      toast.error(formatApiErrorDetail(e.response?.data?.detail) || e.message);
      setBusy(null);
    }
  };

  return (
    <div className="section-pad container-px mx-auto" data-testid="pricing-page">
      <div className="max-w-3xl">
        <div className="overline mb-4">Plans</div>
        <h1 className="font-heading text-5xl sm:text-6xl font-semibold tracking-tight mb-5 leading-none">Simple pricing. Serious impact.</h1>
        <p className="text-lg text-[#5C5A56] leading-relaxed mb-12">No hidden fees. Every subscription funds a charity you choose, plus a monthly prize pool for active players.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 max-w-4xl">
        {PLANS.map((p) => (
          <div key={p.id} className={`card-surface p-10 relative ${p.popular ? "border-[#D95D39] border-2" : ""}`} data-testid={`plan-${p.id}`}>
            {p.popular && (
              <div className="absolute -top-3 left-6 bg-[#D95D39] text-white text-xs uppercase tracking-wider px-3 py-1 rounded-full">Best value</div>
            )}
            <div className="overline mb-2 !text-[#5C5A56]">{p.name}</div>
            <div className="flex items-baseline gap-2 mb-6">
              <span className="font-heading text-6xl font-semibold">${p.price}</span>
              <span className="text-[#5C5A56]">{p.cadence}</span>
            </div>
            <ul className="space-y-3 mb-8">
              {p.perks.map((k, i) => (
                <li key={i} className="flex items-start gap-3 text-sm text-[#1C1B1A]">
                  <Check size={18} className="text-[#D95D39] mt-0.5 flex-shrink-0" /> {k}
                </li>
              ))}
            </ul>
            <button
              onClick={() => subscribe(p.id)}
              disabled={busy === p.id}
              className={`w-full justify-center ${p.popular ? "btn-primary" : "btn-secondary"}`}
              data-testid={`plan-${p.id}-subscribe`}
            >
              {busy === p.id ? "Redirecting to Stripe..." : user ? `Subscribe ${p.name}` : "Sign up & Subscribe"}
            </button>
          </div>
        ))}
      </div>

      <p className="text-xs text-[#8E8D8A] mt-10 max-w-xl">
        Secured by Stripe. Cancel any time from your dashboard. You'll always retain access until your subscription period ends.
      </p>

      {!user && (
        <p className="text-sm text-[#5C5A56] mt-4">
          New here? <Link to="/signup" className="text-[#1E3A2F] font-medium">Create an account first</Link>.
        </p>
      )}
    </div>
  );
}
