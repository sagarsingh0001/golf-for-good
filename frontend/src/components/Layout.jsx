import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { LogOut, Menu, X, User } from "lucide-react";
import { useState } from "react";

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const location = useLocation();
  const nav = useNavigate();
  const hideNav = /^\/(login|signup)$/.test(location.pathname);

  const links = [
    { to: "/", label: "Home" },
    { to: "/how-it-works", label: "How it works" },
    { to: "/charities", label: "Charities" },
    { to: "/pricing", label: "Pricing" },
  ];

  return (
    <div className="App min-h-screen flex flex-col bg-[#F9F8F6]">
      {!hideNav && (
        <header className="fixed top-0 w-full z-50 bg-[#F9F8F6]/90 backdrop-blur-xl border-b border-[#E5E1D8]" data-testid="site-header">
          <div className="container-px mx-auto flex items-center justify-between h-16">
            <Link to="/" className="font-heading font-bold text-xl tracking-tight text-[#1C1B1A]" data-testid="brand-logo">
              Golf<span className="text-[#D95D39]">.</span>ForGood
            </Link>
            <nav className="hidden md:flex items-center gap-8">
              {links.map((l) => (
                <NavLink
                  key={l.to}
                  to={l.to}
                  data-testid={`nav-${l.label.toLowerCase().replace(/\s+/g, "-")}`}
                  className={({ isActive }) =>
                    `text-sm font-medium transition-colors ${isActive ? "text-[#1E3A2F]" : "text-[#5C5A56] hover:text-[#1C1B1A]"}`
                  }
                >
                  {l.label}
                </NavLink>
              ))}
            </nav>
            <div className="hidden md:flex items-center gap-3">
              {user ? (
                <>
                  {user.role === "admin" && (
                    <Link to="/admin" className="text-sm font-medium text-[#1E3A2F] hover:underline" data-testid="nav-admin">Admin</Link>
                  )}
                  <Link to="/dashboard" className="btn-outline !py-2 !px-4 text-sm" data-testid="nav-dashboard">
                    <User size={16} /> Dashboard
                  </Link>
                  <button
                    onClick={async () => { await logout(); nav("/"); }}
                    className="text-[#5C5A56] hover:text-[#1C1B1A] flex items-center gap-1 text-sm"
                    data-testid="nav-logout"
                  >
                    <LogOut size={16} /> Logout
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login" className="text-sm text-[#5C5A56] hover:text-[#1C1B1A]" data-testid="nav-login">Login</Link>
                  <Link to="/signup" className="btn-primary !py-2 !px-5 text-sm" data-testid="nav-signup">Subscribe</Link>
                </>
              )}
            </div>
            <button className="md:hidden" onClick={() => setOpen(!open)} data-testid="nav-mobile-toggle">
              {open ? <X /> : <Menu />}
            </button>
          </div>
          {open && (
            <div className="md:hidden bg-white border-t border-[#E5E1D8] px-6 py-4 flex flex-col gap-4">
              {links.map((l) => (
                <Link key={l.to} to={l.to} onClick={() => setOpen(false)} className="text-[#1C1B1A]">{l.label}</Link>
              ))}
              {user ? (
                <>
                  <Link to="/dashboard" onClick={() => setOpen(false)} className="text-[#1E3A2F] font-medium">Dashboard</Link>
                  {user.role === "admin" && <Link to="/admin" onClick={() => setOpen(false)} className="text-[#1E3A2F]">Admin</Link>}
                  <button onClick={async () => { await logout(); nav("/"); setOpen(false); }} className="text-left text-[#5C5A56]">Logout</button>
                </>
              ) : (
                <>
                  <Link to="/login" onClick={() => setOpen(false)}>Login</Link>
                  <Link to="/signup" onClick={() => setOpen(false)} className="btn-primary inline-block w-fit">Subscribe</Link>
                </>
              )}
            </div>
          )}
        </header>
      )}

      <main className={hideNav ? "" : "pt-16"}>{children}</main>

      {!hideNav && (
        <footer className="bg-[#1E3A2F] text-white mt-24" data-testid="site-footer">
          <div className="container-px mx-auto py-16 grid md:grid-cols-4 gap-10">
            <div>
              <div className="font-heading font-bold text-2xl mb-3">Golf<span className="text-[#D95D39]">.</span>ForGood</div>
              <p className="text-white/70 text-sm leading-relaxed">
                A subscription that turns your golf scores into real-world impact. Play with purpose.
              </p>
            </div>
            <div>
              <div className="overline !text-white/50 mb-3">Product</div>
              <ul className="space-y-2 text-sm text-white/70">
                <li><Link to="/how-it-works">How it works</Link></li>
                <li><Link to="/pricing">Pricing</Link></li>
                <li><Link to="/charities">Charities</Link></li>
              </ul>
            </div>
            <div>
              <div className="overline !text-white/50 mb-3">Account</div>
              <ul className="space-y-2 text-sm text-white/70">
                <li><Link to="/signup">Get started</Link></li>
                <li><Link to="/login">Sign in</Link></li>
                <li><Link to="/dashboard">Dashboard</Link></li>
              </ul>
            </div>
            <div>
              <div className="overline !text-white/50 mb-3">Contact</div>
              <p className="text-white/70 text-sm">hello@golfforgood.co</p>
            </div>
          </div>
          <div className="border-t border-white/10 py-6 text-center text-white/50 text-sm">
            © {new Date().getFullYear()} Golf For Good. All rights reserved.
          </div>
        </footer>
      )}
    </div>
  );
}
