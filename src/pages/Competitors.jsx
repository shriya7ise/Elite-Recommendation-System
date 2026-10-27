import { useState, useEffect, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import gsap from "gsap";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from "chart.js";
import { Bar, Pie } from "react-chartjs-2";
import Layout from "../components/Layout";

// Local UI helpers
const Card = ({ className = "", children, onClick }) => (
  <div
    className={`bg-white rounded-lg shadow-md p-4 ${className}`}
    onClick={onClick}
  >
    {children}
  </div>
);

const Pill = ({ children }) => (
  <span className="inline-block bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full">
    {children}
  </span>
);

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

function parseCsvLine(line) {
  const values = [];
  let current = "";
  let inQuote = false;
  for (let char of line) {
    if (char === '"') inQuote = !inQuote;
    else if (char === "," && !inQuote) {
      values.push(current.trim().replace(/^"|"$/g, "").replace(/"" /g, '"'));
      current = "";
    } else {
      current += char;
    }
  }
  values.push(current.trim().replace(/^"|"$/g, "").replace(/"" /g, '"'));
  return values;
}

function AdCard({ ad, onClick }) {
  return (
    <Card
      className="hover:shadow-lg transition-all cursor-pointer border border-gray-200"
      onClick={onClick}
    >
      <div className="text-sm text-gray-600 font-medium">
        {ad.Platform} • {ad["Ad Type"]}
      </div>
      <h3 className="font-semibold text-lg mt-1 text-gray-900 truncate">{ad.Title}</h3>
      <p className="text-sm text-gray-600 mt-1 line-clamp-3">{ad.Description}</p>
      <div className="text-xs text-gray-500 mt-2">Last analyzed: {ad.Timestamp}</div>
      <div className="mt-3 flex flex-wrap gap-2">
        <Pill>CTR: {ad["Predicted CTR"]}%</Pill>
        <Pill>Quality: {ad["Quality Score"]}/10</Pill>
        <Pill>Engagement: {ad["Engagement Score"]}/10</Pill>
        <Pill>CTA: {ad["CTA Strength"]}</Pill>
      </div>
    </Card>
  );
}

function AdDetail({ ad }) {
  const navigate = useNavigate();

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <button
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
            onClick={() => navigate("/competitors")}
          >
            ← Back to List
          </button>
        </div>

        <Card className="space-y-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{ad.Title}</h1>
            <p className="text-gray-600 mt-2">{ad.Description}</p>
            <div className="text-sm text-gray-500 mt-2">
              {ad.Platform} • {ad["Ad Type"]} • Last analyzed {ad.Timestamp}
            </div>
          </div>

          {/* NLP Analysis and Marketing Effectiveness */}
          <div className="grid md:grid-cols-2 gap-4">
            <Card className="bg-gray-50">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">NLP Analysis</h3>
              <div className="space-y-2 text-sm text-gray-700">
                <p>Sentiment: {ad.Sentiment} (Confidence: {ad["Sentiment Confidence"]})</p>
                <p>Tone: {ad["Emotional Tone"]}</p>
                <p>Reading Level: {ad["Reading Level"]}</p>
                <p>Word/Char Count: {ad["Word Count"]}/{ad["Char Count"]}</p>
              </div>
            </Card>
            <Card className="bg-gray-50">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Marketing Effectiveness</h3>
              <div className="space-y-2 text-sm text-gray-700">
                <p>Engagement: {ad["Engagement Score"]}/10</p>
                <p>Urgency: {ad["Urgency Level"]}</p>
                <p>
                  Triggers:{" "}
                  {ad["Emotional Triggers"]?.length
                    ? ad["Emotional Triggers"].join(", ")
                    : "None"}
                </p>
                <p>Persuasion Elements: {ad["Emotional Triggers"]?.length || 0}</p>
              </div>
            </Card>
          </div>

          {/* Predictions */}
          <div className="grid md:grid-cols-3 gap-4">
            <Card className="text-center">
              <p className="text-xs text-gray-500">Daily Impressions</p>
              <p className="text-xl font-bold text-gray-800">
                {parseInt(ad["Estimated Daily Impressions"] || 0).toLocaleString()}
              </p>
            </Card>
            <Card className="text-center">
              <p className="text-xs text-gray-500">Predicted CPC</p>
              <p className="text-xl font-bold text-gray-800">${ad["Estimated CPC"]}</p>
            </Card>
            <Card className="text-center">
              <p className="text-xs text-gray-500">Quality Score</p>
              <p className="text-xl font-bold text-gray-800">{ad["Quality Score"]}</p>
            </Card>
          </div>

          {/* Competitive Insights */}
          <Card className="bg-gray-50">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Competitive Insights</h3>
            <div className="space-y-2 text-sm text-gray-700">
              <p>Positioning: {ad["Positioning Strategy"]}</p>
              <p>Target Audience: {ad["Target Audience"]}</p>
              <p>
                Key Selling Points:{" "}
                {ad["Key Selling Points"]?.length
                  ? ad["Key Selling Points"].join(", ")
                  : "None"}
              </p>
              <p>
                Advantages:{" "}
                {ad["Competitive Advantages"]?.length
                  ? ad["Competitive Advantages"].join(", ")
                  : "None"}
              </p>
            </div>
          </Card>

          {/* Keyword Analysis */}
          <Card className="bg-gray-50">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Keyword Analysis</h3>
            <div className="space-y-2 text-sm text-gray-700">
              <p>
                Primary Keywords:{" "}
                {ad["Primary Keywords"]?.length
                  ? ad["Primary Keywords"].join(", ")
                  : "None"}
              </p>
              <p>Keyword Density: {ad["Keyword Density"]}%</p>
              <p>
                Missing Opportunities:{" "}
                {ad["Missing Opportunities"]?.length
                  ? ad["Missing Opportunities"].join(", ")
                  : "None"}
              </p>
            </div>
          </Card>

          {/* Recommendations */}
          <Card className="bg-gray-50">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">
              Optimization Recommendations
            </h3>
            <ul className="list-disc pl-5 text-sm text-gray-700 space-y-1">
              {ad["Optimization Recommendations"]?.length ? (
                ad["Optimization Recommendations"].map((r, i) => <li key={i}>{r}</li>)
              ) : (
                <li>No recommendations available</li>
              )}
            </ul>
          </Card>

          <div className="flex justify-end gap-3">
            <button
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
              onClick={() => navigate("/competitors")}
            >
              Close
            </button>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              Export Report
            </button>
          </div>
        </Card>
      </div>
    </Layout>
  );
}

export default function Competitors() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [platform, setPlatform] = useState("All");
  const [sortBy, setSortBy] = useState("Quality Score");
  const [period, setPeriod] = useState("Last 30 days");
  const [performer, setPerformer] = useState("All performers");
  const [ads, setAds] = useState([]);
  const [platformAverages, setPlatformAverages] = useState({});
  const [overall, setOverall] = useState({ ctr: 0, quality: 0, cpc: 0 });
  const [loading, setLoading] = useState(true);

  // Animation refs
  const filtersRef = useRef();
  const adsGridRef = useRef();

  useEffect(() => {
    if (!loading && !id) {
      gsap.fromTo(
        filtersRef.current,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }
      );
      gsap.fromTo(
        adsGridRef.current,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.6, delay: 0.2, ease: "power3.out" }
      );
    }
  }, [loading, id]);

  useEffect(() => {
    setLoading(true);
    fetch("/ad_analysis_results.csv")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch CSV");
        return res.text();
      })
      .then((text) => {
        const lines = text.split("\n").filter((l) => l.trim());
        const headers = parseCsvLine(lines[0]);
        const rows = lines.slice(1).map((l) => {
          const values = parseCsvLine(l);
          return Object.fromEntries(headers.map((h, i) => [h, values[i] || ""]));
        });

        // Remove duplicates by Title + Platform + Description
        const unique = [];
        const seen = new Set();
        rows.sort((a, b) => new Date(b.Timestamp) - new Date(a.Timestamp));
        for (let row of rows) {
          const key = [row.Title, row.Platform, row.Description].join("||");
          if (!seen.has(key)) {
            seen.add(key);
            [
              "Emotional Triggers",
              "Key Selling Points",
              "Competitive Advantages",
              "Primary Keywords",
              "Missing Opportunities",
              "Optimization Recommendations",
            ].forEach((field) => {
              if (row[field]) {
                try {
                  row[field] = JSON.parse(row[field]);
                } catch (e) {
                  row[field] = [];
                }
              } else {
                row[field] = [];
              }
            });
            unique.push(row);
          }
        }
        setAds(unique);

        // Compute platform averages and overall
        const platformGroups = {};
        unique.forEach((ad) => {
          if (!platformGroups[ad.Platform]) platformGroups[ad.Platform] = [];
          platformGroups[ad.Platform].push(ad);
        });

        const averages = {};
        for (let p in platformGroups) {
          const g = platformGroups[p];
          averages[p] = {
            engagement: average(g.map((ad) => parseFloat(ad["Engagement Score"]) || 0)),
            ctr: average(g.map((ad) => parseFloat(ad["Predicted CTR"]) || 0)),
            quality: average(g.map((ad) => parseFloat(ad["Quality Score"]) || 0)),
          };
        }
        setPlatformAverages(averages);

        const allCtr = average(unique.map((ad) => parseFloat(ad["Predicted CTR"]) || 0));
        const allQuality = average(unique.map((ad) => parseFloat(ad["Quality Score"]) || 0));
        const allCpc = average(unique.map((ad) => parseFloat(ad["Estimated CPC"]) || 0));
        setOverall({
          ctr: allCtr.toFixed(1),
          quality: allQuality.toFixed(1),
          cpc: allCpc.toFixed(2),
        });
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching CSV:", err);
        setLoading(false);
      });
  }, []);

  function average(arr) {
    if (!arr.length) return 0;
    return arr.reduce((a, b) => a + b, 0) / arr.length;
  }

  const ctaMap = { Strong: 3, Medium: 2, Weak: 1, None: 0 };

  const getDays = (p) => {
    if (p === "Last 7 days") return 7;
    if (p === "Last 30 days") return 30;
    if (p === "Last 90 days") return 90;
    return Infinity;
  };

  const currentDate = new Date("2025-08-22");

  const list = ads
    .filter((ad) => {
      const adDate = new Date(ad.Timestamp);
      const daysDiff = (currentDate - adDate) / (1000 * 3600 * 24);
      return (
        daysDiff <= getDays(period) &&
        (platform === "All" || ad.Platform === platform) &&
        (performer === "All performers" ||
          ad["Engagement Potential"] === performer.toLowerCase())
      );
    })
    .sort((a, b) => {
      if (sortBy === "Quality Score")
        return parseFloat(b["Quality Score"]) - parseFloat(a["Quality Score"]);
      if (sortBy === "Engagement")
        return parseFloat(b["Engagement Score"]) - parseFloat(a["Engagement Score"]);
      if (sortBy === "CTA Strength")
        return ctaMap[b["CTA Strength"]] - ctaMap[a["CTA Strength"]];
      return 0;
    });

  if (loading) {
    return (
      <Layout>
        <div className="min-h-[50vh] flex items-center justify-center">
          <div className="text-lg text-gray-600">Loading...</div>
        </div>
      </Layout>
    );
  }

  if (id) {
    const selectedAd = ads.find((ad) => ad.ID === id);
    if (!selectedAd) {
      return (
        <Layout>
          <div className="min-h-[50vh] flex items-center justify-center">
            <div className="text-lg text-red-600">Ad not found</div>
          </div>
        </Layout>
      );
    }
    return <AdDetail ad={selectedAd} />;
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Competitor Intelligence Dashboard
          </h1>
        </div>

        {/* Visualizations */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              Average Engagement by Platform
            </h2>
            <div className="h-64">
              <Bar
                data={{
                  labels: Object.keys(platformAverages),
                  datasets: [
                    {
                      label: "Engagement Score",
                      data: Object.values(platformAverages).map((a) => a.engagement),
                      backgroundColor: "rgba(75, 192, 192, 0.6)",
                      borderColor: "rgba(75, 192, 192, 1)",
                      borderWidth: 1,
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                      title: { display: true, text: "Engagement Score" },
                    },
                    x: { title: { display: true, text: "Platform" } },
                  },
                  plugins: {
                    legend: { display: false },
                    tooltip: { backgroundColor: "#1f2937" },
                  },
                }}
              />
            </div>
          </Card>
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              Ad Distribution by Platform
            </h2>
            <div className="h-64">
              <Pie
                data={{
                  labels: Object.keys(platformAverages),
                  datasets: [
                    {
                      data: Object.keys(platformAverages).map(
                        (p) => ads.filter((ad) => ad.Platform === p).length
                      ),
                      backgroundColor: ["#3b82f6", "#f97316", "#10b981", "#ef4444"],
                      borderColor: ["#ffffff"],
                      borderWidth: 1,
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: { position: "bottom" },
                    tooltip: { backgroundColor: "#1f2937" },
                  },
                }}
              />
            </div>
          </Card>
        </div>

        {/* Filters */}
        <div ref={filtersRef}>
          <Card className="p-6 mb-8">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Filter Ads</h2>
            <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm text-gray-600 mb-1">Platform</label>
                <select
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={platform}
                  onChange={(e) => setPlatform(e.target.value)}
                >
                  <option>All</option>
                  {Object.keys(platformAverages).map((p) => (
                    <option key={p}>{p}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Sort By</label>
                <select
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                >
                  <option>Quality Score</option>
                  <option>Engagement</option>
                  <option>CTA Strength</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Time Period</label>
                <select
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={period}
                  onChange={(e) => setPeriod(e.target.value)}
                >
                  <option>Last 30 days</option>
                  <option>Last 7 days</option>
                  <option>Last 90 days</option>
                  <option>All time</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Performance</label>
                <select
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={performer}
                  onChange={(e) => setPerformer(e.target.value)}
                >
                  <option>All performers</option>
                  <option>high</option>
                  <option>medium</option>
                  <option>low</option>
                </select>
              </div>
            </div>
          </Card>
        </div>

        {/* Ad Grid */}
        <div ref={adsGridRef}>
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Competitor Ads</h2>
          {list.length === 0 ? (
            <Card className="p-6 text-center text-gray-600">
              No ads match the selected filters.
            </Card>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {list.map((ad) => (
                <AdCard
                  key={ad.ID}
                  ad={ad}
                  onClick={() => navigate(`/competitors/${ad.ID}`)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}