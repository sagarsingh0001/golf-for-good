import { NavLink, Outlet, useLocation } from "react-router-dom";
import { Home, Target, Trophy, Heart, UserCog, Shield } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

const items = [
  { to: "/dashboard", icon: Home, label: "Overview" },
  { to: "/dashboard/scores", icon: Target, label: "Scores" },
  { to: "/dashboard/draws", icon: Trophy, label: "Draws" },
  { to: "/dashboard/winnings", icon: Heart, label: "Winnings" },
  { to: "/dashboard/profile", icon: UserCog, label: "Profile" },
];

const adminItems = [
  { to: "/admin", icon: Shield, label: "Overview" },
  { to: "/admin/users", icon: UserCog, label: "Users" },
  { to: "/admin/draws", icon: Trophy, label: "Draws" },
  { to: "/admin/charities", icon: Heart, label: "Charities" },
  { to: "/admin/winners", icon: Target, label: "Winners" },
];

export default function DashboardShell({ children, admin = false }) {
  const { user } = useAuth();
  const list = admin ? adminItems : items;
  return (
    <div className="container-px mx-auto py-10 grid md:grid-cols-12 gap-8" data-testid={admin ? "admin-shell" : "dashboard-shell"}>
      <aside className="md:col-span-3">
        <div className="card-surface p-6 sticky top-24">
          <div className="overline mb-3">{admin ? "Admin Panel" : "Your account"}</div>
          <div className="font-heading text-lg font-medium mb-1 truncate">{user?.name}</div>
          <div className="text-xs text-[#8E8D8A] mb-6 truncate">{user?.email}</div>
          <nav className="flex flex-col gap-1">
            {list.map((i) => (
              <NavLink
                key={i.to}
                to={i.to}
                end
                className={({ isActive }) =>
                  `flex items-center gap-3 text-sm px-3 py-2 rounded-lg transition-colors ${isActive ? "bg-[#1E3A2F] text-white" : "text-[#1C1B1A] hover:bg-[#F0EFEA]"}`
                }
                data-testid={`${admin ? "admin" : "dash"}-link-${i.label.toLowerCase()}`}
              >
                <i.icon size={16} /> {i.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </aside>
      <div className="md:col-span-9">{children}</div>
    </div>
  );
}
