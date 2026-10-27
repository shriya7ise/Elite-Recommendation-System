import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Landing from "./pages/Landing";
import CampaignHub from "./pages/CampaignHub";
import Dashboard from "./pages/Dashboard";
import Competitors from "./pages/Competitors";
import Insights from "./pages/Insights";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/campaigns" element={<CampaignHub />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/competitors" element={<Competitors />} />
        <Route path="/insights" element={<Insights />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
