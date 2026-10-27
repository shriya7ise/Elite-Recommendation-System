import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import CampaignHub from "./pages/CampaignHub";
import Dashboard from "./pages/Dashboard";
import CompetitorIntel from "./pages/CompetitorIntel";
import Competitors from "./pages/Competitors"; // legacy CSV ad explorer
import Recommendations from "./pages/Recommendations";
import AdStudio from "./pages/AdStudio";
import Insights from "./pages/Insights";

const Home = () => { const { user } = useAuth(); return <Navigate to={user ? "/dashboard" : "/login"} replace />; };
const P = ({ children }) => <ProtectedRoute>{children}</ProtectedRoute>;

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<P><Dashboard /></P>} />
          <Route path="/competitors" element={<P><CompetitorIntel /></P>} />
          <Route path="/competitors/ads" element={<P><Competitors /></P>} />
          <Route path="/recommendations" element={<P><Recommendations /></P>} />
          <Route path="/studio" element={<P><AdStudio /></P>} />
          <Route path="/insights" element={<P><Insights /></P>} />
          <Route path="/campaigns" element={<P><CampaignHub /></P>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
