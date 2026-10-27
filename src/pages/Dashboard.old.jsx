import { Card, Stat } from "../components/UI";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend
} from "recharts";
import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import Papa from "papaparse";
import Layout from "../components/Layout";

export default function Dashboard() {
  const [campaignData, setCampaignData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const topCardsRef = useRef();
  const chartsRef = useRef();
  const campaignsRef = useRef();
  const metricsRef = useRef();

  // Safe parsing for numeric values
  const safeParseFloat = (value) => {
    const parsed = parseFloat(value);
    return isNaN(parsed) ? 0 : parsed;
  };

  // Local file upload for testing
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      console.log("Uploading local CSV:", file.name);
      Papa.parse(file, {
        header: true,
        complete: (result) => {
          console.log("Local CSV Data:", result.data);
          setCampaignData(result.data);
          setIsLoading(false);
        },
        error: (err) => {
          console.error("Local Parse Error:", err.message);
          setError(`Failed to parse CSV: ${err.message}`);
          setIsLoading(false);
        },
      });
    }
  };

  // Fetch CSV
  useEffect(() => {
    console.log("Attempting to fetch /ad_analysis_results.csv");
    Papa.parse("/ad_analysis_results.csv", {
      download: true,
      header: true,
      complete: (result) => {
        console.log("Parsed CSV Data:", result.data);
        if (result.data.length === 0 || !result.data[0].Platform) {
          console.warn("CSV is empty or invalid");
          setError("CSV file is empty or invalid");
        } else {
          setCampaignData(result.data);
        }
        setIsLoading(false);
      },
      error: (err) => {
        console.error("PapaParse Error:", err.message);
        setError(`Failed to load CSV: ${err.message || "Unknown error"}`);
        setIsLoading(false);
      },
    });
  }, []);

  // Animations
  useEffect(() => {
    if (!isLoading && !error) {
      gsap.fromTo(topCardsRef.current, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" });
      gsap.fromTo(chartsRef.current, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.6, delay: 0.2, ease: "power3.out" });
      gsap.fromTo(campaignsRef.current, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.6, delay: 0.4, ease: "power3.out" });
      gsap.fromTo(metricsRef.current, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.6, delay: 0.6, ease: "power3.out" });
    }
  }, [isLoading, error]);

  // Aggregate data for visualizations
  const platformRevenue = campaignData.reduce((acc, curr) => {
    const platform = curr.Platform || "Unknown";
    const cost = safeParseFloat(curr["Estimated CPC"]) * safeParseFloat(curr["Estimated Daily Impressions"]);
    const existing = acc.find((p) => p.name === platform);
    if (existing) {
      existing.value += cost;
    } else {
      acc.push({ name: platform, value: cost });
    }
    return acc;
  }, []);

  const platformMetrics = campaignData.reduce((acc, curr) => {
    const platform = curr.Platform || "Unknown";
    const ctr = safeParseFloat(curr["Predicted CTR"]);
    const cpc = safeParseFloat(curr["Estimated CPC"]);
    const cvr = safeParseFloat(curr["Engagement Score"]);
    const existing = acc.find((p) => p.name === platform);
    if (existing) {
      existing.CTR += ctr;
      existing.CPC += cpc;
      existing.CVR += cvr;
      existing.count += 1;
    } else {
      acc.push({ name: platform, CTR: ctr, CPC: cpc, CVR: cvr, count: 1 });
    }
    return acc;
  }, []).map((p) => ({
    name: p.name,
    CTR: p.count ? p.CTR / p.count : 0,
    CPC: p.count ? p.CPC / p.count : 0,
    CVR: p.count ? p.CVR / p.count : 0,
  }));

  const totalRevenue = platformRevenue.reduce((a, b) => a + b.value, 0);
  const activeCampaigns = campaignData.length;
  const averageROI = campaignData.length
    ? campaignData.reduce((sum, curr) => sum + safeParseFloat(curr["Engagement Score"]), 0) / campaignData.length
    : 0;
  const averageCPA = campaignData.length
    ? campaignData.reduce((sum, curr) => sum + safeParseFloat(curr["Estimated CPC"]), 0) / campaignData.length
    : 0;

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"];

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[50vh]">
          <div className="text-lg text-gray-600">Loading...</div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[50vh]">
          <div className="text-lg text-red-600">{error}</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Company Dashboard</h1>
        </div>

        {/* File input for local CSV testing */}
        <div className="mb-4">
          <input type="file" accept=".csv" onChange={handleFileUpload} className="text-sm" />
        </div>

        {/* Top cards */}
        <div ref={topCardsRef} className="grid md:grid-cols-4 gap-4">
          <Stat label="Total Revenue" value={`$${Math.round(totalRevenue).toLocaleString()}`} sub="+12% MoM"/>
          <Stat label="Active Campaigns" value={activeCampaigns} sub="Across Platforms"/>
          <Stat label="Average ROI" value={`${Math.round(averageROI)}%`} sub="Based on Engagement"/>
          <Stat label="Average CPA" value={`$${Math.round(averageCPA)}`} sub="Benchmark: $50"/>
        </div>

        {/* Platform performance */}
        <div ref={chartsRef} className="grid md:grid-cols-2 gap-4 mt-6">
          <Card>
            <div className="text-sm text-gray-500 mb-2">Revenue Distribution by Platform</div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={platformRevenue} dataKey="value" nameKey="name" outerRadius={90} label>
                    {platformRevenue.map((_, i) => (
                      <Cell key={`cell-${i}`} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `$${Math.round(value).toLocaleString()}`} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-3 text-sm text-gray-600">
              {platformRevenue.map((p) => (
                <div key={p.name} className="flex justify-between">
                  <span>{p.name}</span><span>${Math.round(p.value).toLocaleString()}</span>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <div className="text-sm text-gray-500 mb-2">Platform Metrics</div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={platformMetrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name"/>
                  <YAxis />
                  <Tooltip formatter={(value, name) => name === "CTR" || name === "CVR" ? `${value.toFixed(2)}%` : `$${value.toFixed(2)}`} />
                  <Legend />
                  <Bar dataKey="CTR" fill="#0088FE" name="CTR (%)" />
                  <Bar dataKey="CPC" fill="#00C49F" name="CPC ($)" />
                  <Bar dataKey="CVR" fill="#FFBB28" name="Engagement Score" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>

        {/* Active campaigns grid */}
        <div ref={campaignsRef} className="mt-6">
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {campaignData.slice(0, 6).map((campaign, i) => (
              <Card key={campaign.ID || i} className="overflow-hidden">
                <div className="h-24 bg-gradient-to-r from-gray-100 to-gray-200"/>
                <div className="mt-3 flex items-center justify-between">
                  <div>
                    <div className="font-semibold">{campaign.Title || `Campaign #${i + 1}`}</div>
                    <div className="text-xs text-gray-500">
                      {campaign.Platform} • CTR {safeParseFloat(campaign["Predicted CTR"]).toFixed(1)}% • CPC ${safeParseFloat(campaign["Estimated CPC"]).toFixed(2)}
                    </div>
                  </div>
                  <div
                    className={`w-2.5 h-2.5 rounded-full ${
                      safeParseFloat(campaign["Engagement Score"]) > 50
                        ? "bg-green-500"
                        : safeParseFloat(campaign["Engagement Score"]) > 20
                        ? "bg-yellow-500"
                        : "bg-red-500"
                    }`}
                  />
                </div>
                <div className="mt-3 flex gap-2">
                  <button className="px-2 py-1 rounded-lg bg-gray-100 text-xs">Pause</button>
                  <button className="px-2 py-1 rounded-lg bg-gray-100 text-xs">Optimize</button>
                  <button className="px-2 py-1 rounded-lg bg-gray-100 text-xs">View</button>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Real-time metrics */}
        <div ref={metricsRef} className="grid md:grid-cols-4 gap-4 mt-6">
          <Card>
            <div className="text-xs text-gray-500">Live Spend Rate</div>
            <div className="text-xl font-bold mt-1">
              ${Math.round(
                campaignData.reduce((sum, curr) => sum + safeParseFloat(curr["Estimated CPC"]) * safeParseFloat(curr["Estimated Daily Impressions"]) / 24, 0)
              )}/hr
            </div>
          </Card>
          <Card>
            <div className="text-xs text-gray-500">Impressions / Hour</div>
            <div className="text-xl font-bold mt-1">
              {Math.round(
                campaignData.reduce((sum, curr) => sum + safeParseFloat(curr["Estimated Daily Impressions"]) / 24, 0)
              ).toLocaleString()}
            </div>
          </Card>
          <Card>
            <div className="text-xs text-gray-500">Conversions</div>
            <div className="text-xl font-bold mt-1">
              {Math.round(
                campaignData.reduce((sum, curr) => sum + safeParseFloat(curr["Engagement Score"]) * 10, 0)
              )}
            </div>
          </Card>
          <Card>
            <div className="text-xs text-gray-500">Budget Alerts</div>
            <div className="text-xl font-bold mt-1 text-yellow-600">
              {campaignData.filter((c) => safeParseFloat(c["Quality Score"]) < 3).length} warnings
            </div>
          </Card>
        </div>
      </div>
    </Layout>
  );
}