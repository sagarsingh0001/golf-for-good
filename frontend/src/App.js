import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { Toaster } from "@/components/ui/sonner";
import Layout from "@/components/Layout";

import Landing from "@/pages/Landing";
import Pricing from "@/pages/Pricing";
import Login from "@/pages/Login";
import Signup from "@/pages/Signup";
import HowItWorks from "@/pages/HowItWorks";
import Charities from "@/pages/Charities";
import CharityDetail from "@/pages/CharityDetail";
import Dashboard from "@/pages/dashboard/Dashboard";
import ScoresPage from "@/pages/dashboard/Scores";
import DrawsPage from "@/pages/dashboard/Draws";
import WinningsPage from "@/pages/dashboard/Winnings";
import ProfilePage from "@/pages/dashboard/Profile";
import CheckoutSuccess from "@/pages/CheckoutSuccess";
import AdminDashboard from "@/pages/admin/AdminDashboard";
import AdminUsers from "@/pages/admin/AdminUsers";
import AdminDraws from "@/pages/admin/AdminDraws";
import AdminCharities from "@/pages/admin/AdminCharities";
import AdminWinners from "@/pages/admin/AdminWinners";

function Protected({ children, role }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen flex items-center justify-center text-[#5C5A56]" data-testid="loading-indicator">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (role === "admin" && user.role !== "admin") return <Navigate to="/dashboard" replace />;
  return children;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/how-it-works" element={<HowItWorks />} />
            <Route path="/charities" element={<Charities />} />
            <Route path="/charities/:id" element={<CharityDetail />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/checkout/success" element={<Protected><CheckoutSuccess /></Protected>} />
            <Route path="/dashboard" element={<Protected><Dashboard /></Protected>} />
            <Route path="/dashboard/scores" element={<Protected><ScoresPage /></Protected>} />
            <Route path="/dashboard/draws" element={<Protected><DrawsPage /></Protected>} />
            <Route path="/dashboard/winnings" element={<Protected><WinningsPage /></Protected>} />
            <Route path="/dashboard/profile" element={<Protected><ProfilePage /></Protected>} />
            <Route path="/admin" element={<Protected role="admin"><AdminDashboard /></Protected>} />
            <Route path="/admin/users" element={<Protected role="admin"><AdminUsers /></Protected>} />
            <Route path="/admin/draws" element={<Protected role="admin"><AdminDraws /></Protected>} />
            <Route path="/admin/charities" element={<Protected role="admin"><AdminCharities /></Protected>} />
            <Route path="/admin/winners" element={<Protected role="admin"><AdminWinners /></Protected>} />
          </Routes>
        </Layout>
        <Toaster richColors position="top-right" />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
