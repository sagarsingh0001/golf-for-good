import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import Marquee from "react-fast-marquee";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ArrowRight, Heart, Trophy, Target } from "lucide-react";

export default function Landing() {
  const [featured, setFeatured] = useState([]);
  const [charities, setCharities] = useState([]);

  useEffect(() => {
    api.get("/charities/featured").then((r) => setFeatured(r.data)).catch(() => {});
    api.get("/charities").then((r) => setCharities(r.data.slice(0, 3))).catch(() => {});
  }, []);

  return (
    <div data-testid="landing-page">
      {/* HERO */}
      <section className="relative min-h-[92vh] flex items-end overflow-hidden">
        <div className="absolute inset-0">
          <img
            src="https://images.pexels.com/photos/6646926/pexels-photo-6646926.jpeg"
            alt=""
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#1E3A2F]/80 via-[#1E3A2F]/40 to-transparent" />
        </div>
        <div className="relative container-px mx-auto pb-24 text-white">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
            className="max-w-3xl"
          >
            <div className="overline !text-[#D95D39] mb-6" data-testid="hero-overline">A subscription with a conscience</div>
            <h1 className="font-heading font-bold text-5xl sm:text-7xl leading-[0.95] tracking-tight mb-6" data-testid="hero-title">
              Play your round.<br />
              <span className="text-[#D95D39]">Change</span> someone's life.
            </h1>
            <p className="text-lg sm:text-xl text-white/85 max-w-2xl mb-8">
              Track your Stableford scores. Support a charity you believe in. Win from a monthly prize pool. One subscription — three things that matter.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link to="/signup" className="btn-primary" data-testid="hero-cta-signup">
                Start for $9.99/mo <ArrowRight size={18} />
              </Link>
              <Link to="/how-it-works" className="text-white/90 underline underline-offset-8 decoration-white/30 hover:decoration-white self-center" data-testid="hero-link-how">
                How it works →
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* MARQUEE */}
      <div className="bg-[#EBE6DD] border-y border-[#E5E1D8] py-5" data-testid="marquee-stats">
        <Marquee gradient={false} speed={35}>
          <div className="flex items-center gap-12 mx-6 font-mono-display text-sm text-[#1E3A2F]">
            <span>★ 8 verified charities</span>
            <span>★ 10% minimum charitable contribution</span>
            <span>★ Monthly jackpot rollover</span>
            <span>★ Zero admin overhead</span>
            <span>★ Backed by a community that plays for a purpose</span>
            <span>★ Stableford scoring, 1–45</span>
          </div>
        </Marquee>
      </div>

      {/* HOW IT WORKS */}
      <section className="section-pad container-px mx-auto" data-testid="how-section">
        <div className="grid md:grid-cols-12 gap-12 items-start">
          <div className="md:col-span-4">
            <div className="overline mb-4">Three simple steps</div>
            <h2 className="font-heading text-4xl sm:text-5xl leading-none font-semibold tracking-tight">A subscription that gives twice.</h2>
          </div>
          <div className="md:col-span-8 grid sm:grid-cols-3 gap-6">
            {[
              { icon: <Heart className="text-[#D95D39]" />, title: "Subscribe", text: "Pick monthly or yearly. Choose a charity you care about. Minimum 10% of every dollar you pay goes to them — automatically." },
              { icon: <Target className="text-[#D95D39]" />, title: "Enter your scores", text: "Log your last 5 rounds in Stableford format. One entry per day. Your latest five replace the oldest." },
              { icon: <Trophy className="text-[#D95D39]" />, title: "Win & give", text: "Monthly draws match your scores against winning numbers. Match 3, 4 or all 5 to claim from the prize pool." },
            ].map((s, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="card-surface p-8"
                data-testid={`how-step-${i}`}
              >
                <div className="mb-4">{s.icon}</div>
                <div className="font-heading text-xl font-medium mb-2">{i + 1}. {s.title}</div>
                <p className="text-[#5C5A56] text-sm leading-relaxed">{s.text}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* FEATURED CHARITY */}
      {featured[0] && (
        <section className="bg-[#EBE6DD] section-pad" data-testid="featured-charity-section">
          <div className="container-px mx-auto grid md:grid-cols-12 gap-12 items-center">
            <div className="md:col-span-6">
              <img src={featured[0].image_url} alt={featured[0].name} className="rounded-2xl w-full h-[480px] object-cover" />
            </div>
            <div className="md:col-span-6">
              <div className="overline mb-4">Spotlight</div>
              <h2 className="font-heading text-4xl sm:text-5xl leading-none font-semibold tracking-tight mb-5">{featured[0].name}</h2>
              <p className="text-[#5C5A56] text-lg leading-relaxed mb-6">{featured[0].description}</p>
              <Link to={`/charities/${featured[0].id}`} className="btn-secondary" data-testid="featured-charity-cta">
                Meet this charity <ArrowRight size={16} />
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* CHARITY PREVIEW */}
      <section className="section-pad container-px mx-auto">
        <div className="flex items-end justify-between mb-10">
          <div>
            <div className="overline mb-4">Choose a cause</div>
            <h2 className="font-heading text-4xl sm:text-5xl leading-none font-semibold tracking-tight">Real organizations. Real impact.</h2>
          </div>
          <Link to="/charities" className="text-[#1E3A2F] font-medium hidden sm:inline-flex items-center gap-1" data-testid="charities-view-all">View all <ArrowRight size={16} /></Link>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {charities.map((c) => (
            <Link key={c.id} to={`/charities/${c.id}`} className="card-surface overflow-hidden block" data-testid={`charity-card-${c.id}`}>
              <img src={c.image_url} alt={c.name} className="w-full h-56 object-cover" />
              <div className="p-6">
                <div className="overline !text-[#5C5A56] mb-2">{c.category}</div>
                <h3 className="font-heading text-xl font-medium mb-2">{c.name}</h3>
                <p className="text-[#5C5A56] text-sm leading-relaxed">{c.short_description}</p>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* FINAL CTA */}
      <section className="relative section-pad overflow-hidden" data-testid="final-cta">
        <div className="absolute inset-0">
          <img
            src="https://images.unsplash.com/photo-1758599670006-d7fe945b5966?crop=entropy&cs=srgb&fm=jpg"
            alt=""
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-[#1C1B1A]/65" />
        </div>
        <div className="relative container-px mx-auto text-center text-white">
          <h2 className="font-heading text-5xl sm:text-6xl font-semibold tracking-tight mb-6 max-w-3xl mx-auto leading-none">
            Your next round could change everything.
          </h2>
          <p className="text-white/85 max-w-xl mx-auto mb-8 text-lg">
            Start your subscription today. Your first charitable contribution lands within 60 seconds.
          </p>
          <Link to="/signup" className="btn-primary" data-testid="final-cta-signup">Join Golf For Good <ArrowRight size={18} /></Link>
        </div>
      </section>
    </div>
  );
}
