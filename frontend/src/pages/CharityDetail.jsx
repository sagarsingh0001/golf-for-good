import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "@/lib/api";
import { ArrowLeft } from "lucide-react";

export default function CharityDetail() {
  const { id } = useParams();
  const [c, setC] = useState(null);

  useEffect(() => {
    api.get(`/charities/${id}`).then((r) => setC(r.data)).catch(() => {});
  }, [id]);

  if (!c) return <div className="section-pad container-px mx-auto" data-testid="charity-loading">Loading charity...</div>;

  return (
    <div data-testid="charity-detail">
      <div className="relative h-[50vh] min-h-[360px]">
        <img src={c.image_url} alt={c.name} className="w-full h-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30" />
        <div className="absolute inset-0 flex items-end container-px pb-10">
          <div className="text-white max-w-3xl">
            <Link to="/charities" className="inline-flex items-center gap-2 text-white/80 hover:text-white mb-4 text-sm" data-testid="charity-back">
              <ArrowLeft size={16} /> All charities
            </Link>
            <div className="overline !text-[#D95D39] mb-3">{c.category}</div>
            <h1 className="font-heading text-5xl sm:text-6xl font-semibold tracking-tight">{c.name}</h1>
          </div>
        </div>
      </div>
      <div className="section-pad container-px mx-auto grid md:grid-cols-12 gap-12">
        <div className="md:col-span-8">
          <p className="text-lg text-[#1C1B1A] leading-relaxed mb-6">{c.description}</p>
          {c.events?.length > 0 && (
            <>
              <h3 className="font-heading text-2xl font-medium mt-10 mb-4">Upcoming events</h3>
              <ul className="space-y-2 text-[#5C5A56]">
                {c.events.map((e, i) => <li key={i}>• {e.title || e.name || JSON.stringify(e)}</li>)}
              </ul>
            </>
          )}
        </div>
        <aside className="md:col-span-4">
          <div className="card-surface p-8 sticky top-24">
            <div className="overline mb-3">Support {c.name}</div>
            <p className="text-[#5C5A56] text-sm mb-6">Direct your subscription contribution to this charity every month.</p>
            <Link to="/signup" className="btn-primary w-full justify-center" data-testid="charity-cta-support">Subscribe &amp; support</Link>
          </div>
        </aside>
      </div>
    </div>
  );
}
