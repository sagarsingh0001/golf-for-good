import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { CheckCircle2, Loader2 } from "lucide-react";

export default function CheckoutSuccess() {
  const [params] = useSearchParams();
  const sessionId = params.get("session_id");
  const [status, setStatus] = useState("polling");
  const [tries, setTries] = useState(0);
  const { refresh } = useAuth();
  const nav = useNavigate();

  useEffect(() => {
    if (!sessionId) return;
    let stopped = false;
    const poll = async (n = 0) => {
      if (stopped || n >= 12) {
        setStatus("timeout");
        return;
      }
      try {
        const { data } = await api.get(`/subscribe/status/${sessionId}`);
        if (data.payment_status === "paid") {
          setStatus("paid");
          await refresh();
          return;
        }
        if (data.status === "expired") {
          setStatus("expired");
          return;
        }
        setTries(n + 1);
        setTimeout(() => poll(n + 1), 2000);
      } catch {
        setTimeout(() => poll(n + 1), 2000);
      }
    };
    poll();
    return () => { stopped = true; };
  }, [sessionId, refresh]);

  return (
    <div className="section-pad container-px mx-auto text-center max-w-xl mx-auto" data-testid="checkout-success-page">
      {status === "polling" && (
        <>
          <Loader2 className="mx-auto animate-spin text-[#D95D39]" size={48} />
          <h1 className="font-heading text-3xl font-semibold mt-6 mb-3">Confirming your subscription...</h1>
          <p className="text-[#5C5A56]">Attempt {tries + 1}. This should only take a few seconds.</p>
        </>
      )}
      {status === "paid" && (
        <>
          <CheckCircle2 className="mx-auto text-[#5B7B5A]" size={64} />
          <h1 className="font-heading text-4xl font-semibold mt-6 mb-3">You're in!</h1>
          <p className="text-[#5C5A56] mb-8">Your subscription is active. Your charity thanks you.</p>
          <button onClick={() => nav("/dashboard")} className="btn-primary" data-testid="checkout-continue">Go to dashboard</button>
        </>
      )}
      {(status === "timeout" || status === "expired") && (
        <>
          <h1 className="font-heading text-3xl font-semibold mb-3">We couldn't confirm your payment.</h1>
          <p className="text-[#5C5A56] mb-8">If you were charged, it will reflect in your dashboard shortly. Otherwise, try again.</p>
          <button onClick={() => nav("/pricing")} className="btn-primary">Back to pricing</button>
        </>
      )}
    </div>
  );
}
