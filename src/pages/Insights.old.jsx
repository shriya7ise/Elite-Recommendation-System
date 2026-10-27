import React, { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";
import Layout from "../components/Layout";

// Simple UI helpers
const Card = ({ children, className = "", ...props }) => (
  <div
    className={`bg-gray-50 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow ${className}`}
    {...props}
  >
    {children}
  </div>
);

const CardContent = ({ children, className = "", ...props }) => (
  <div className={`p-4 ${className}`} {...props}>
    {children}
  </div>
);

const Button = ({
  children,
  onClick,
  disabled = false,
  className = "",
  variant = "primary",
  ...props
}) => {
  const base =
    "px-4 py-2 rounded-md font-medium text-sm transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2";
  const variants = {
    primary:
      "bg-blue-100 text-blue-800 hover:bg-blue-200 focus:ring-blue-300 disabled:bg-gray-200 disabled:text-gray-500",
    secondary:
      "bg-gray-100 text-gray-800 hover:bg-gray-200 focus:ring-gray-300 disabled:bg-gray-200 disabled:text-gray-500",
    success:
      "bg-green-100 text-green-800 hover:bg-green-200 focus:ring-green-300 disabled:bg-gray-200 disabled:text-gray-500",
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${variants[variant]} ${
        disabled ? "cursor-not-allowed" : "cursor-pointer"
      } ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

export default function Insights() {
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState("");

  const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  const testConnection = async () => {
    try {
      const response = await fetch(`${API_URL}/`);
      return response.ok;
    } catch {
      return false;
    }
  };

  const loadTestInsights = async () => {
    setLoading(true);
    setError(null);
    setStatus("");
    try {
      const response = await fetch(`${API_URL}/test-insights`);
      const data = await response.json();
      if (data.error) {
        setError(data.error);
        setInsights([]);
      } else {
        setInsights(data.insights || []);
        setStatus("Test insights loaded successfully!");
      }
    } catch {
      setError(
        "Failed to load test insights. Is the backend running on port 8000?"
      );
      setInsights([]);
    }
    setLoading(false);
  };

  const generateInsights = async () => {
    setLoading(true);
    setError(null);
    setStatus("Generating insights...");
    try {
      const response = await fetch(`${API_URL}/insight_gen`, {
        method: "POST",
      });
      const data = await response.json();
      if (data.error) {
        setError(data.error);
        setInsights([]);
        setStatus("");
      } else {
        setInsights(data.insights || []);
        setStatus("Insights generated successfully!");
      }
    } catch {
      setError("Failed to generate insights. Check backend connection.");
      setInsights([]);
      setStatus("");
    }
    setLoading(false);
  };

  useEffect(() => {
    testConnection();
  }, []);

  const chartData = insights.map((insight, idx) => ({
    name: `Insight ${idx + 1}`,
    value: Math.min(insight.length, 100),
    score: Math.floor(Math.random() * 100) + 1,
    type: insight.startsWith("Positive") ? "Positive" : "Negative",
  }));

  return (
    <Layout>
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-3">
            AI-Powered Marketing Insights
          </h1>
          <p className="text-gray-600">
            Generate insights from pre-loaded competitor and campaign data
          </p>
        </div>

        {/* Action Buttons */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-5">
          <h2 className="text-xl font-medium mb-4 text-center text-gray-800">
            Generate Insights
          </h2>
          <div className="flex justify-center gap-4 flex-wrap">
            <Button onClick={generateInsights} disabled={loading}>
              {loading ? "Generating..." : "Generate AI Insights"}
            </Button>
            <Button
              onClick={loadTestInsights}
              disabled={loading}
              variant="success"
            >
              {loading ? "Loading..." : "Try Test Insights"}
            </Button>
          </div>

          {status && (
            <div className="mt-3 p-2 bg-green-50 border border-green-100 text-green-700 rounded-md text-center text-sm">
              {status}
            </div>
          )}
        </div>

        {error && (
          <div className="bg-red-50 border border-red-100 text-red-700 px-4 py-2 rounded-md text-center text-sm">
            {error}
          </div>
        )}

        {loading && (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-3"></div>
            <p>AI is analyzing your data...</p>
          </div>
        )}

        {insights.length > 0 && !loading && (
          <>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {insights.map((insight, idx) => {
                const isPositive = insight.startsWith("Positive");
                return (
                  <Card
                    key={idx}
                    className={`h-full border ${
                      isPositive ? "border-green-100" : "border-red-100"
                    }`}
                  >
                    <CardContent>
                      <div
                        className={`text-xs font-semibold mb-2 ${
                          isPositive ? "text-green-700" : "text-red-700"
                        }`}
                      >
                        {isPositive ? "POSITIVE" : "NEGATIVE"}
                      </div>
                      <p className="text-sm text-gray-800">{insight}</p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* Simple charts */}
            <div className="grid md:grid-cols-2 gap-6 mt-8">
              <Card>
                <CardContent>
                  <h3 className="font-medium mb-4">Insight Length Overview</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" fill="#3b82f6" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
}