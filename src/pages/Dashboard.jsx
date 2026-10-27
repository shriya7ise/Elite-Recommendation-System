import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import Layout from "../components/Layout";
import { Card, Stat } from "../components/UI";
import { api } from "../lib/api";
import { useAuth } from "../context/AuthContext";

const COLORS = ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed"];

export default function Dashboard() {
  const { business, user } = useAuth();
  const [d, setD] = useState(null);
  const [err, setErr] = useState("");
  useEffect(() => { api("/campaigns").then(setD).catch((e) => setErr(e.message)); }, []);
  if (err) return <Layout><p className="text-red-600">{err}</p></Layout>;
  if (!d) return <Layout><p className="text-gray-500">Loading…</p></Layout>;

  const cs = d.campaigns;
  const spend = cs.reduce((s, c) => s + c.spend, 0);
  const avgRoi = cs.length ? cs.reduce((s, c) => s + c.roi, 0) / cs.length : 0;
  return (
    <Layout>
      <div className="max-w-6xl mx-auto space-y-6">
        <div><h1 className="text-2xl font-bold">{business.company} dashboard</h1>
          <p className="text-sm text-gray-500">Welcome, {user.name}{user.role_title ? ` · ${user.role_title}` : ""} · simulated performance data</p></div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <Stat label="Total spend" value={spend.toLocaleString()} />
          <Stat label="Avg ROI" value={`${avgRoi.toFixed(0)}%`} />
          <Stat label="Running" value={cs.filter((c) => c.status === "Running").length} sub={`of ${cs.length} campaigns`} />
          <Stat label="Impressions" value={cs.reduce((s, c) => s + c.impressions, 0).toLocaleString()} />
        </div>
        <div className="grid lg:grid-cols-2 gap-4">
          <Card><h3 className="font-semibold mb-2">Monthly spend (k)</h3>
            <ResponsiveContainer width="100%" height={240}><BarChart data={d.monthly_spend}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="month" /><YAxis /><Tooltip /><Bar dataKey="spend" fill="#2563eb" radius={4} /></BarChart></ResponsiveContainer></Card>
          <Card><h3 className="font-semibold mb-2">Revenue by platform</h3>
            <ResponsiveContainer width="100%" height={240}><PieChart><Pie data={d.platforms} dataKey="revenue" nameKey="name" label>{d.platforms.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer></Card>
        </div>
        <Card><h3 className="font-semibold mb-2">Campaigns</h3>
          <div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr className="text-left text-gray-500"><th>Name</th><th>Platform</th><th>Status</th><th>Budget</th><th>ROI</th><th>CTR</th><th>CPC</th><th>CVR</th><th>Score</th></tr></thead>
            <tbody>{cs.map((c) => <tr key={c.id} className="border-t"><td className="py-2 font-medium">{c.name}</td><td>{c.platform}</td><td>{c.status}</td><td>{c.budget.toLocaleString()}</td><td>{c.roi}%</td><td>{c.ctr}%</td><td>{c.cpc}</td><td>{c.cvr}%</td><td>{c.score}</td></tr>)}</tbody></table></div></Card>
      </div>
    </Layout>
  );
}
