import React from "react";
import { Card, Stat, Pill } from "../components/UI";
import { campaigns, monthlySpend } from "../data/mock";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import {
  Play,
  PlusCircle,
  Import,
  Wand2,
  Loader2,
  Download,
  Eye,
  Settings,
} from "lucide-react";
import { useMemo, useState, useEffect } from "react";
import Layout from "../components/Layout";

const statusColor = (s) =>
  s === "Running"
    ? "text-green-600 bg-green-50"
    : s === "Paused"
    ? "text-yellow-600 bg-yellow-50"
    : "text-gray-600 bg-gray-50";

// Backend API URL - adjust this to your backend URL
const API_BASE_URL = "http://localhost:8000";

export default function CampaignHub() {
  const [filters, setFilters] = useState({ platform: "All", perf: "All" });
  const [formData, setFormData] = useState({
    productName: "",
    targetAudience: "",
    budgetRange: "",
    platform: "Meta",
    aiLevel: "AI: Copy + Visuals + Targeting",
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedAds, setGeneratedAds] = useState([]);
  const [showAdsModal, setShowAdsModal] = useState(false);
  const [showApiModal, setShowApiModal] = useState(false);
  const [placidApiKey, setPlacidApiKey] = useState("");
  const [placidTemplate, setPlacidTemplate] = useState("");
  const [useBackend, setUseBackend] = useState(true); // Default to backend mode
  const [templateFields, setTemplateFields] = useState(null);
  const [showTemplateInfo, setShowTemplateInfo] = useState(false);

  // Load API key from memory state (no localStorage)
  useEffect(() => {
    // Initialize with empty values - user needs to configure
    setPlacidApiKey("");
    setPlacidTemplate("");
  }, []);

  const filtered = useMemo(() => {
    return campaigns.filter(
      (c) => filters.platform === "All" || c.platform === filters.platform
    );
  }, [filters]);

  const avgRoi = Math.round(
    filtered.reduce((a, c) => a + c.roi, 0) / (filtered.length || 1)
  );

  // Check backend health
  const checkBackendHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return response.ok;
    } catch (error) {
      console.error("Backend health check failed:", error);
      return false;
    }
  };

  // Backend API Integration
  const generateAdWithBackend = async (templateData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/generate-ad`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          template_id: placidTemplate,
          modifications: templateData,
          create_now: true,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.detail || `Backend error! status: ${response.status}`
        );
      }

      const data = await response.json();
      return data.image_url;
    } catch (error) {
      console.error("Backend API error:", error);
      throw error;
    }
  };

  // Direct Placid API Integration (frontend)
  const generateAdWithPlacid = async (templateData) => {
    if (!placidApiKey) {
      throw new Error("Placid API key not configured");
    }

    try {
      const response = await fetch(
        `https://api.placid.app/api/rest/${placidTemplate}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${placidApiKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            create_now: true,
            modifications: templateData,
          }),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `Placid API error! status: ${response.status} - ${errorText}`
        );
      }

      const data = await response.json();
      return data.image_url;
    } catch (error) {
      console.error("Placid API error:", error);
      throw error;
    }
  };

  // Generate single ad variation (instead of multiple)
  const generateAdImage = async () => {
    // Single variation with primary style
    const templateData = {
      "talk title": formData.productName, // Product name → talk title
      "speaker name": formData.targetAudience, // Target audience → speaker name
      cta: "Shop Now", // Fixed CTA button
      info: formData.budgetRange || "5k-20k",
      color_primary: "#3B82F6",
      color_secondary: "#1E40AF",
    };

    const generateFunction = useBackend
      ? generateAdWithBackend
      : generateAdWithPlacid;

    try {
      const imageUrl = await generateFunction(templateData);
      return imageUrl;
    } catch (error) {
      console.error("Failed to generate ad:", error);
      return null;
    }
  };

  // Fallback image generation for demo purposes (single image)
  const generateFallbackImage = () => {
    return `https://via.placeholder.com/512x512/3B82F6/FFFFFF?text=${encodeURIComponent(
      formData.productName
    )}`;
  };

  // Generate Campaign Handler with better debugging
  const handleGenerateCampaign = async () => {
    if (!formData.productName || !formData.targetAudience) {
      alert("Please fill in product name and target audience");
      return;
    }

    if (!useBackend && (!placidApiKey || !placidTemplate)) {
      alert(
        "Please configure Placid API key and template ID in settings, or enable backend mode"
      );
      setShowApiModal(true);
      return;
    }

    if (useBackend && !placidTemplate) {
      alert("Please configure template ID for backend mode");
      setShowApiModal(true);
      return;
    }

    // First, let's check what fields your template has
    console.log("🔍 Checking template fields before generation...");

    setIsGenerating(true);

    try {
      let image;

      try {
        console.log(
          `🎨 Generating ad with ${
            useBackend ? "Backend" : "Direct Placid"
          } API...`
        );
        console.log(`📝 Form Data:`, formData);

        image = await generateAdImage();

        if (!image) {
          throw new Error("No image generated from API");
        }
      } catch (apiError) {
        console.error("❌ API failed, using fallback:", apiError);
        image = generateFallbackImage();
        alert(
          `API generation failed: ${apiError.message}. Using placeholder image for demo.\n\nTip: Click '📋 Check Template' to see what fields your template expects.`
        );
      }

      // Create campaign data with single image
      const newCampaign = {
        id: Date.now(),
        name: `${formData.productName} Campaign`,
        platform: formData.platform,
        status: "Draft",
        budget: parseInt(formData.budgetRange.split("-")[0]) * 1000 || 5000,
        roi: Math.floor(Math.random() * 100) + 50,
        score: Math.floor(Math.random() * 3) + 7,
        images: [image], // Single image instead of array of 3
        createdAt: new Date().toISOString(),
        audience: formData.targetAudience,
        aiLevel: formData.aiLevel,
      };

      setGeneratedAds([newCampaign]);
      setShowAdsModal(true);

      console.log("✅ Campaign generated successfully:", newCampaign);
    } catch (error) {
      console.error("❌ Campaign generation failed:", error);
      alert(`Failed to generate campaign: ${error.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  // API Configuration Handler
  const handleSaveApiConfig = () => {
    if (!useBackend && !placidApiKey.trim()) {
      alert("Please enter a valid Placid API key or enable backend mode");
      return;
    }

    if (!placidTemplate.trim()) {
      alert("Please enter a valid Placid template ID");
      return;
    }

    // Store in component state (no localStorage)
    setShowApiModal(false);
    alert("API configuration saved successfully!");
  };

  // Test backend connection
  const testBackendConnection = async () => {
    try {
      const isHealthy = await checkBackendHealth();
      if (isHealthy) {
        alert("✅ Backend connection successful!");
      } else {
        alert(
          "❌ Backend is not responding. Please check if it's running on " +
            API_BASE_URL
        );
      }
    } catch (error) {
      alert("❌ Failed to connect to backend: " + error.message);
    }
  };

  // Test template fields
  const getTemplateFields = async () => {
    if (!placidTemplate) {
      alert("Please enter a template ID first");
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/template-info/${placidTemplate}`
      );
      if (response.ok) {
        const data = await response.json();
        setTemplateFields(data);
        setShowTemplateInfo(true);
        console.log("Template info:", data);
      } else {
        const error = await response.json();
        alert(`Failed to get template info: ${error.detail}`);
      }
    } catch (error) {
      alert(`Error getting template info: ${error.message}`);
    }
  };

  // Test single field mapping
  const testSingleField = async (fieldName, fieldValue) => {
    if (!placidTemplate) {
      alert("Please configure template ID first");
      return;
    }

    const testData = {
      [fieldName]: fieldValue,
    };

    console.log(`🧪 Testing field: ${fieldName} = ${fieldValue}`);

    try {
      const generateFunction = useBackend
        ? generateAdWithBackend
        : generateAdWithPlacid;
      const imageUrl = await generateFunction(testData);

      if (imageUrl) {
        // Show the test image
        window.open(imageUrl, "_blank");
        alert(
          `✅ Test successful! Field '${fieldName}' appears to work. Check the opened image.`
        );
      }
    } catch (error) {
      console.error(`Test failed for field '${fieldName}':`, error);
      alert(`Test failed for field '${fieldName}': ${error.message}`);
    }
  };

  const runFieldTests = async () => {
    if (!formData.productName) {
      alert("Please enter a product name first to use for testing");
      return;
    }

    const commonFieldNames = [
      "title",
      "headline",
      "product_name",
      "productName",
      "name",
      "subtitle",
      "description",
      "target_audience",
      "targetAudience",
      "audience",
      "cta",
      "call_to_action",
      "button_text",
      "buttonText",
      "action",
      "text",
      "main_text",
      "content",
      "copy",
    ];

    alert(
      "🧪 Starting field tests... This will test common field names one by one. Check your browser for new tabs opening."
    );

    for (const fieldName of commonFieldNames.slice(0, 5)) {
      // Test first 5 to avoid spam
      console.log(`Testing field: ${fieldName}`);
      await new Promise((resolve) => setTimeout(resolve, 1000)); // Wait 1 second between tests

      try {
        await testSingleField(fieldName, formData.productName);
      } catch (error) {
        console.log(`Field ${fieldName} failed:`, error.message);
      }
    }

    alert(
      "✅ Field tests completed! Check the opened tabs to see which fields worked."
    );
  };

  // Form input handlers
  const handleInputChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  // Download image handler
  const handleDownloadImage = async (imageUrl, index) => {
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `ad-creative-${index + 1}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Download failed:", error);
      alert(
        'Download failed. Please try right-clicking and selecting "Save Image As"'
      );
    }
  };

  // View image handler
  const handleViewImage = (imageUrl, index) => {
    window.open(imageUrl, "_blank");
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Campaign Hub</h1>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={testBackendConnection}
              className="flex items-center gap-2 px-4 py-2 text-gray-600 border rounded-xl hover:bg-gray-50"
            >
              🔌 Test Backend
            </button>
            <button
              onClick={getTemplateFields}
              className="flex items-center gap-2 px-4 py-2 text-gray-600 border rounded-xl hover:bg-gray-50"
            >
              📋 Check Template
            </button>
            <button
              onClick={runFieldTests}
              className="flex items-center gap-2 px-4 py-2 text-orange-600 border border-orange-200 rounded-xl hover:bg-orange-50"
            >
              🧪 Test Fields
            </button>
            <button
              onClick={() => setShowApiModal(true)}
              className="flex items-center gap-2 px-4 py-2 text-gray-600 border rounded-xl hover:bg-gray-50"
            >
              <Settings size={16} />
              API Settings
            </button>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-3 gap-4 mb-6">
          <button className="flex items-center gap-2 justify-center rounded-2xl border bg-white p-4 hover:bg-gray-50 transition-colors">
            <Wand2 size={18} /> Generate from competitor analysis
          </button>
          <button className="flex items-center gap-2 justify-center rounded-2xl border bg-white p-4 hover:bg-gray-50 transition-colors">
            <PlusCircle size={18} /> Create custom campaign
          </button>
          <button className="flex items-center gap-2 justify-center rounded-2xl border bg-white p-4 hover:bg-gray-50 transition-colors">
            <Import size={18} /> Import for optimization
          </button>
        </div>

        {/* AI Campaign Generation Form */}
        <Card className="mt-5">
          <div className="grid md:grid-cols-5 gap-4">
            <input
              className="border rounded-xl px-3 py-2"
              placeholder="Product name / category"
              value={formData.productName}
              onChange={(e) => handleInputChange("productName", e.target.value)}
            />
            <input
              className="border rounded-xl px-3 py-2"
              placeholder="Target audience"
              value={formData.targetAudience}
              onChange={(e) =>
                handleInputChange("targetAudience", e.target.value)
              }
            />
            <input
              className="border rounded-xl px-3 py-2"
              placeholder="Budget range (e.g. 5k-20k)"
              value={formData.budgetRange}
              onChange={(e) => handleInputChange("budgetRange", e.target.value)}
            />
            <select
              className="border rounded-xl px-3 py-2"
              value={formData.platform}
              onChange={(e) => handleInputChange("platform", e.target.value)}
            >
              <option>Meta</option>
              <option>Google</option>
              <option>LinkedIn</option>
            </select>
            <select
              className="border rounded-xl px-3 py-2"
              value={formData.aiLevel}
              onChange={(e) => handleInputChange("aiLevel", e.target.value)}
            >
              <option>AI: Copy + Visuals + Targeting</option>
              <option>AI: Copy only</option>
              <option>AI: Targeting only</option>
            </select>
          </div>
          <div className="mt-4 flex justify-between items-center">
            <div className="text-sm text-gray-500">
              {useBackend
                ? placidTemplate
                  ? "✅ Backend mode - Template configured"
                  : "⚠️ Configure template ID for backend"
                : placidApiKey
                ? "✅ Direct API mode - Placid configured"
                : "⚠️ Configure Placid API credentials"}
            </div>
            <button
              className="px-4 py-2 bg-blue-600 text-white rounded-xl flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors"
              onClick={handleGenerateCampaign}
              disabled={isGenerating}
            >
              {isGenerating ? (
                <>
                  <Loader2 size={16} className="animate-spin" /> Generating...
                </>
              ) : (
                <>
                  <Play size={16} /> Generate Campaign
                </>
              )}
            </button>
          </div>
        </Card>

        {/* Stats */}
        <div className="grid md:grid-cols-4 gap-4 mt-6">
          <Stat label="Total Campaigns" value={filtered.length} sub="+2 this month" />
          <Stat label="Average ROI" value={`${avgRoi}%`} sub="↑ vs last month" />
          <Stat label="Best Platform" value="Google" sub="ROI 148%, CPC $2.6" />
          <Card>
            <div className="text-sm text-gray-500 mb-2">
              Monthly spend vs last month
            </div>
            <div className="h-28">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={monthlySpend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="spend" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3 mt-8">
          <select
            className="border rounded-xl px-3 py-2 bg-white"
            value={filters.platform}
            onChange={(e) =>
              setFilters((f) => ({ ...f, platform: e.target.value }))
            }
          >
            <option>All</option>
            <option>Meta</option>
            <option>Google</option>
            <option>LinkedIn</option>
          </select>
          <select
            className="border rounded-xl px-3 py-2 bg-white"
            value={filters.perf}
            onChange={(e) =>
              setFilters((f) => ({ ...f, perf: e.target.value }))
            }
          >
            <option>All</option>
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>
        </div>

        {/* Table */}
        <Card className="mt-4 overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="text-left text-gray-500">
              <tr>
                <th className="py-2">Name</th>
                <th>Platform</th>
                <th>Status</th>
                <th>Budget</th>
                <th>ROI%</th>
                <th>Success Score</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody className="[&>tr:not(:last-child)]:border-b">
              {filtered.map((row) => (
                <tr key={row.id} className="hover:bg-gray-50">
                  <td className="py-2 font-medium">{row.name}</td>
                  <td>{row.platform}</td>
                  <td>
                    <span
                      className={`px-2 py-1 rounded-full text-xs ${statusColor(
                        row.status
                      )}`}
                    >
                      {row.status}
                    </span>
                  </td>
                  <td>${row.budget.toLocaleString()}</td>
                  <td>{row.roi}%</td>
                  <td>{row.score}/10</td>
                  <td className="space-x-2">
                    <Pill>Pause</Pill>
                    <Pill>Optimize</Pill>
                    <Pill>View</Pill>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>

        {/* Template Info Modal */}
        {showTemplateInfo && templateFields && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-bold">
                    Template Field Information
                  </h2>
                  <button
                    onClick={() => setShowTemplateInfo(false)}
                    className="text-gray-500 hover:text-gray-700 text-xl"
                  >
                    ×
                  </button>
                </div>

                <div className="space-y-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-blue-800 mb-2">
                      Template Details
                    </h3>
                    <p>
                      <strong>Name:</strong> {templateFields.name || "N/A"}
                    </p>
                    <p>
                      <strong>ID:</strong> {placidTemplate}
                    </p>
                    <p>
                      <strong>Width:</strong> {templateFields.width || "N/A"}px
                    </p>
                    <p>
                      <strong>Height:</strong> {templateFields.height || "N/A"}px
                    </p>
                  </div>

                  {templateFields.layers && (
                    <div>
                      <h3 className="font-semibold mb-3">
                        Available Fields (Layers)
                      </h3>
                      <div className="grid grid-cols-1 gap-3">
                        {templateFields.layers
                          .filter((layer) => layer.name) // Only show named layers
                          .map((layer, index) => (
                            <div key={index} className="border rounded-lg p-3">
                              <div className="flex justify-between items-start mb-2">
                                <span className="font-medium text-gray-800">
                                  {layer.name}
                                </span>
                                <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                                  {layer.type}
                                </span>
                              </div>

                              {layer.type === "text" && (
                                <div className="text-sm text-gray-600">
                                  <p>Default: "{layer.text || "Empty"}"</p>
                                  {layer.fontSize && (
                                    <p>Font Size: {layer.fontSize}px</p>
                                  )}
                                  {layer.color && <p>Color: {layer.color}</p>}
                                </div>
                              )}

                              {layer.type === "image" && (
                                <div className="text-sm text-gray-600">
                                  <p>Image layer - can be replaced with URL</p>
                                </div>
                              )}
                            </div>
                          ))}
                      </div>
                    </div>
                  )}

                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-yellow-800 mb-2">
                      💡 Tips
                    </h3>
                    <ul className="text-sm text-yellow-700 space-y-1">
                      <li>
                        • Use the <strong>layer name</strong> as the field key
                        in your API calls
                      </li>
                      <li>• Text layers can be modified with string values</li>
                      <li>• Image layers can be replaced with image URLs</li>
                      <li>
                        • Make sure your form data matches these field names
                      </li>
                    </ul>
                  </div>
                </div>

                <div className="flex justify-end mt-6">
                  <button
                    onClick={() => setShowTemplateInfo(false)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700"
                  >
                    Got it!
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* API Configuration Modal */}
        {showApiModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-2xl max-w-md w-full">
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-bold">API Configuration</h2>
                  <button
                    onClick={() => setShowApiModal(false)}
                    className="text-gray-500 hover:text-gray-700 text-xl"
                  >
                    ×
                  </button>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center gap-3 mb-4">
                    <input
                      type="checkbox"
                      id="useBackend"
                      checked={useBackend}
                      onChange={(e) => setUseBackend(e.target.checked)}
                      className="rounded"
                    />
                    <label htmlFor="useBackend" className="text-sm font-medium">
                      Use Backend API (Recommended)
                    </label>
                  </div>

                  {!useBackend && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Placid API Key (Direct Mode)
                      </label>
                      <input
                        type="password"
                        className="w-full border rounded-xl px-3 py-2"
                        placeholder="Enter your Placid API key"
                        value={placidApiKey}
                        onChange={(e) => setPlacidApiKey(e.target.value)}
                      />
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Template ID
                    </label>
                    <input
                      type="text"
                      className="w-full border rounded-xl px-3 py-2"
                      placeholder="Enter your Placid template ID"
                      value={placidTemplate}
                      onChange={(e) => setPlacidTemplate(e.target.value)}
                    />
                  </div>

                  <div className="text-xs text-gray-500">
                    <p>
                      • Get your API key from{" "}
                      <a
                        href="https://placid.app"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        placid.app
                      </a>
                    </p>
                    <p>• Create a template and copy its ID</p>
                    <p>
                      • Backend mode is more secure (API key stored on server)
                    </p>
                    <p>• Backend URL: {API_BASE_URL}</p>
                  </div>
                </div>

                <div className="flex justify-end gap-3 mt-6">
                  <button
                    onClick={() => setShowApiModal(false)}
                    className="px-4 py-2 text-gray-600 border rounded-xl hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSaveApiConfig}
                    className="px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700"
                  >
                    Save Configuration
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Generated Ads Modal */}
        {showAdsModal && generatedAds.length > 0 && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold">Generated Ad Creative</h2>
                  <button
                    onClick={() => setShowAdsModal(false)}
                    className="text-gray-500 hover:text-gray-700 text-xl"
                  >
                    ×
                  </button>
                </div>

                {generatedAds.map((campaign) => (
                  <div key={campaign.id} className="mb-8">
                    <h3 className="text-lg font-semibold mb-4">
                      {campaign.name}
                    </h3>
                    <div className="flex justify-center">
                      {campaign.images.map((image, index) => (
                        <div key={index} className="relative group max-w-md">
                          <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                            <img
                              src={image}
                              alt={`Ad creative ${index + 1}`}
                              className="w-full h-full object-cover"
                              onError={(e) => {
                                e.target.src = `https://via.placeholder.com/512x512/6B7280/FFFFFF?text=Failed+to+Load`;
                              }}
                            />
                          </div>
                          <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-200 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100">
                            <div className="flex gap-2">
                              <button
                                onClick={() =>
                                  handleDownloadImage(image, index)
                                }
                                className="p-2 bg-white rounded-full hover:bg-gray-100"
                                title="Download"
                              >
                                <Download size={16} />
                              </button>
                              <button
                                onClick={() => handleViewImage(image, index)}
                                className="p-2 bg-white rounded-full hover:bg-gray-100"
                                title="View Full Size"
                              >
                                <Eye size={16} />
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}

                <div className="flex justify-end gap-3 mt-6">
                  <button
                    onClick={() => setShowAdsModal(false)}
                    className="px-4 py-2 text-gray-600 border rounded-xl hover:bg-gray-50"
                  >
                    Close
                  </button>
                  <button className="px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700">
                    Create Campaign
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}