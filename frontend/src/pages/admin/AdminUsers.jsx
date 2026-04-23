import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import DashboardShell from "@/components/DashboardShell";
import { toast } from "sonner";

export default function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [q, setQ] = useState("");
  const load = () => api.get("/admin/users", { params: { q: q || undefined } }).then((r) => setUsers(r.data));
  useEffect(() => { load(); }, [q]);

  const toggleSub = async (u) => {
    const next = u.subscription_status === "active" ? "cancelled" : "active";
    await api.patch(`/admin/users/${u.id}`, { subscription_status: next });
    toast.success(`Subscription set to ${next}`);
    load();
  };

  return (
    <DashboardShell admin>
      <div data-testid="admin-users">
        <h1 className="font-heading text-4xl font-semibold tracking-tight mb-6">Users</h1>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search by name or email..." className="w-full max-w-md bg-white border border-[#E5E1D8] rounded-full px-5 py-3 mb-6" data-testid="admin-users-search" />
        <div className="card-surface overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-[#F0EFEA] text-left text-[#5C5A56] uppercase text-xs">
              <tr><th className="p-4">Name</th><th className="p-4">Email</th><th className="p-4">Role</th><th className="p-4">Subscription</th><th className="p-4">Actions</th></tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-t border-[#E5E1D8]" data-testid={`admin-user-row-${u.id}`}>
                  <td className="p-4 font-medium">{u.name}</td>
                  <td className="p-4 text-[#5C5A56]">{u.email}</td>
                  <td className="p-4 capitalize">{u.role}</td>
                  <td className="p-4"><span className={`px-3 py-1 rounded-full text-xs ${u.subscription_status === "active" ? "bg-[#5B7B5A] text-white" : "bg-[#EBE6DD] text-[#5C5A56]"}`}>{u.subscription_status}</span></td>
                  <td className="p-4">
                    <button onClick={() => toggleSub(u)} className="text-[#D95D39] text-sm font-medium" data-testid={`admin-toggle-sub-${u.id}`}>
                      {u.subscription_status === "active" ? "Cancel" : "Activate"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </DashboardShell>
  );
}
