import { motion } from "framer-motion";
import { Link } from "react-router-dom";

export default function HowItWorks() {
  return (
    <div className="section-pad container-px mx-auto" data-testid="how-page">
      <div className="overline mb-4">How it works</div>
      <h1 className="font-heading text-5xl sm:text-6xl font-semibold tracking-tight mb-4 leading-none">Every score has a story.</h1>
      <p className="text-lg text-[#5C5A56] max-w-2xl leading-relaxed mb-16">
        Here's the full picture — from signup to charity contribution to the moment your numbers are drawn.
      </p>

      <div className="grid md:grid-cols-12 gap-12">
        {[
          { t: "Subscribe", d: "Choose monthly or yearly. Select one of our verified charities and set your contribution between 10–100% of your subscription. Stripe handles all billing." },
          { t: "Enter scores", d: "Log your last 5 golf rounds. Each must be in Stableford format (1–45). Only one score per date. New scores replace the oldest — always the most recent 5 count." },
          { t: "Monthly draw", d: "At month-end, 5 winning numbers (1–45) are drawn. Match 3, 4, or all 5 of your scores to win. If nobody hits 5, the jackpot rolls forward." },
          { t: "Prize pool", d: "50% of every subscription funds the prize pool. It splits 40% / 35% / 25% across the 5-match, 4-match, and 3-match tiers. Multiple winners share equally." },
          { t: "Verify & get paid", d: "Winners upload a screenshot of their scorecard. Admin verifies, payout is processed. Pending → Paid." },
          { t: "Charity impact", d: "Your charity receives its allocation every period. You can see your cumulative contribution on your dashboard." },
        ].map((s, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.08 }}
            className="md:col-span-6 card-surface p-10"
            data-testid={`how-item-${i}`}
          >
            <div className="font-mono-display text-[#D95D39] text-sm mb-3">0{i + 1}</div>
            <h3 className="font-heading text-2xl font-medium mb-3">{s.t}</h3>
            <p className="text-[#5C5A56] leading-relaxed">{s.d}</p>
          </motion.div>
        ))}
      </div>

      <div className="mt-20 text-center">
        <Link to="/pricing" className="btn-primary" data-testid="how-cta-pricing">See pricing</Link>
      </div>
    </div>
  );
}
