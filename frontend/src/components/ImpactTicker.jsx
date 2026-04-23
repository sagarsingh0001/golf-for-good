import { useEffect, useState, useRef } from "react";
import { api } from "@/lib/api";

function useInView(ref) {
  const [seen, setSeen] = useState(false);
  useEffect(() => {
    if (!ref.current) return;
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setSeen(true); io.disconnect(); } }, { threshold: 0.3 });
    io.observe(ref.current);
    return () => io.disconnect();
  }, [ref]);
  return seen;
}

function Counter({ to, prefix = "", suffix = "", decimals = 0 }) {
  const ref = useRef(null);
  const inView = useInView(ref);
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!inView) return;
    const dur = 1400;
    const start = performance.now();
    const tick = (t) => {
      const p = Math.min(1, (t - start) / dur);
      const eased = 1 - Math.pow(1 - p, 3);
      setVal(Number(to) * eased);
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [inView, to]);
  const formatted = decimals > 0 ? val.toFixed(decimals) : Math.floor(val).toLocaleString();
  return <span ref={ref} className="font-heading font-bold">{prefix}{formatted}{suffix}</span>;
}

export default function ImpactTicker() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.get("/public/stats").then((r) => setStats(r.data)).catch(() => setStats(null));
  }, []);

  if (!stats) return null;

  const cards = [
    { label: "Active players", value: stats.active_subscribers, testid: "ticker-active" },
    { label: "Charities supported", value: stats.total_charities, testid: "ticker-charities" },
    { label: "Into charity so far", value: stats.charity_contribution_total, prefix: "$", decimals: 2, testid: "ticker-charity-total" },
    { label: "Prizes awarded", value: stats.total_prizes_paid, prefix: "$", decimals: 2, testid: "ticker-prizes" },
  ];

  return (
    <section className="section-pad container-px mx-auto" data-testid="impact-ticker">
      <div className="grid md:grid-cols-12 gap-10 items-end mb-10">
        <div className="md:col-span-5">
          <div className="overline mb-4">The numbers</div>
          <h2 className="font-heading text-4xl sm:text-5xl font-semibold tracking-tight leading-none">
            Real impact. Tracked live.
          </h2>
        </div>
        <div className="md:col-span-6 md:col-start-7">
          <p className="text-[#5C5A56] text-lg leading-relaxed">
            Every subscription funds a cause. Every draw rewards a player. Here's where the movement stands right now.
          </p>
        </div>
      </div>

      <div className="grid md:grid-cols-4 gap-4">
        {cards.map((c) => (
          <div key={c.label} className="card-surface p-8 flex flex-col" data-testid={c.testid}>
            <div className="overline !text-[#5C5A56] mb-4">{c.label}</div>
            <div className="text-5xl sm:text-6xl leading-none text-[#1E3A2F]">
              <Counter to={c.value} prefix={c.prefix || ""} decimals={c.decimals || 0} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
