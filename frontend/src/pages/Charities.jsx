import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Link } from "react-router-dom";
import { Search } from "lucide-react";

export default function Charities() {
  const [items, setItems] = useState([]);
  const [q, setQ] = useState("");
  const [cat, setCat] = useState("all");

  useEffect(() => {
    api.get("/charities", { params: { q: q || undefined, category: cat !== "all" ? cat : undefined } })
      .then((r) => setItems(r.data));
  }, [q, cat]);

  const categories = ["all", "Environment", "Education", "Hunger", "Animals", "Community"];

  return (
    <div className="section-pad container-px mx-auto" data-testid="charities-page">
      <div className="overline mb-4">Our charities</div>
      <h1 className="font-heading text-5xl sm:text-6xl font-semibold tracking-tight mb-4 leading-none">8 causes. One choice.</h1>
      <p className="text-lg text-[#5C5A56] max-w-2xl leading-relaxed mb-10">Pick the one that moves you. You can change it any time from your dashboard.</p>

      <div className="flex flex-col sm:flex-row gap-4 mb-10">
        <div className="relative flex-1 max-w-md">
          <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-[#8E8D8A]" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search charities..."
            className="w-full bg-white border border-[#E5E1D8] rounded-full pl-11 pr-4 py-3 focus:outline-none focus:border-[#D95D39]"
            data-testid="charities-search"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => setCat(c)}
              className={`px-4 py-2 rounded-full text-sm border transition-colors ${cat === c ? "bg-[#1E3A2F] text-white border-[#1E3A2F]" : "bg-white text-[#1C1B1A] border-[#E5E1D8] hover:border-[#1E3A2F]"}`}
              data-testid={`charity-filter-${c}`}
            >
              {c === "all" ? "All" : c}
            </button>
          ))}
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {items.map((c) => (
          <Link key={c.id} to={`/charities/${c.id}`} className="card-surface overflow-hidden block" data-testid={`charity-item-${c.id}`}>
            <img src={c.image_url} alt={c.name} className="w-full h-56 object-cover" />
            <div className="p-6">
              <div className="overline !text-[#5C5A56] mb-2">{c.category}</div>
              <h3 className="font-heading text-xl font-medium mb-2">{c.name}</h3>
              <p className="text-[#5C5A56] text-sm leading-relaxed line-clamp-3">{c.short_description}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
