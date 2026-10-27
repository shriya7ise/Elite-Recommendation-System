import Layout from "../components/Layout";
import { Card } from "../components/UI";
import { Rocket, Target, Brain, Lightbulb } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import gsap from "gsap";

// ✅ Features list
const features = [
  { icon: Target, title: "Multi-Platform Monitoring", desc: "Track ads across Meta, Google, LinkedIn" },
  { icon: Brain, title: "AI Campaign Creation", desc: "Generate ad copies, targeting, budget allocation" },
  { icon: Rocket, title: "Smart Analytics", desc: "NLP + Computer Vision competitor analysis" },
  { icon: Lightbulb, title: "Predictive Insights", desc: "AI recommendations before you launch" },
];

const Chatbot = () => {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hi! Ask me about marketing campaigns or business knowledge." }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const chatWindowRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Animate + autoscroll
  useEffect(() => {
    gsap.fromTo(
      chatWindowRef.current,
      { opacity: 0, x: -50 },
      { opacity: 1, x: 0, duration: 0.6, ease: "power3.out" }
    );
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ✅ Send message via backend API
  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input, session_id: "user1" }),
      });

      const data = await res.json();
      const botResponse = { sender: "bot", text: data.answer || "Error: " + data.error };
      setMessages(prev => [...prev, botResponse]);
    } catch (err) {
      setMessages(prev => [...prev, { sender: "bot", text: "Backend not reachable." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      ref={chatWindowRef}
      className="bg-white w-full h-full rounded-lg shadow-xl flex flex-col relative"
    >
      <div className="absolute top-4 right-4">
        <span className="text-lg font-semibold text-blue-600">Marketing Assistant</span>
      </div>
      <div className="flex-1 p-6 pt-12 overflow-y-auto max-h-[calc(100vh-200px)]">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`mb-4 ${msg.sender === "user" ? "text-right" : "text-left"}`}
          >
            <span
              className={`inline-block p-3 rounded-lg ${
                msg.sender === "user" ? "bg-blue-100" : "bg-gray-100"
              }`}
            >
              {msg.text}
            </span>
          </div>
        ))}
        {isLoading && (
          <div className="text-left mb-4">
            <span className="inline-block p-3 rounded-lg bg-gray-100">
              Thinking...
            </span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="p-4 border-t">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
          placeholder="Ask about marketing or business..."
          disabled={isLoading}
        />
      </div>
    </div>
  );
};

export default function Landing() {
  const heroRef = useRef();
  const featuresRef = useRef();
  const howItWorksRef = useRef();
  const chatbotRef = useRef();

  useEffect(() => {
    gsap.fromTo(heroRef.current, { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 0.8, ease: "power3.out" });
    gsap.fromTo(featuresRef.current, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.6, delay: 0.3, ease: "power3.out" });
    gsap.fromTo(howItWorksRef.current, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.6, delay: 0.5, ease: "power3.out" });
    gsap.fromTo(chatbotRef.current, { opacity: 0, x: -50 }, { opacity: 1, x: 0, duration: 0.6, ease: "power3.out" });
  }, []);

  return (
    <Layout>
      <div className="flex flex-col md:flex-row min-h-screen">
        {/* Chatbot */}
        <aside
          ref={chatbotRef}
          className="w-full md:w-80 bg-gray-50 p-4 md:p-6 md:h-screen"
        >
          <Chatbot />
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-4 md:p-6">
          {/* Hero */}
          <section ref={heroRef} className="text-center py-20 bg-gradient-to-b from-blue-50 to-white">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">
              AI-Powered Competitive Marketing Intelligence
            </h1>
            <p className="text-lg md:text-xl text-gray-600 mb-8">
              Monitor competitor ads, create winning campaigns, maximize ROI
            </p>
            <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition">
              Start Free Trial
            </button>
          </section>

          {/* Features */}
          <section ref={featuresRef} className="py-16 bg-gray-50">
            <div className="container mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {features.map(({ icon: Icon, title, desc }) => (
                <Card key={title}>
                  <div className="p-6 text-center">
                    <Icon className="mx-auto mb-4 text-blue-600" size={40} />
                    <h3 className="text-xl font-semibold mb-2">{title}</h3>
                    <p className="text-gray-600">{desc}</p>
                  </div>
                </Card>
              ))}
            </div>
          </section>

          {/* How It Works */}
          <section ref={howItWorksRef} className="py-16">
            <div className="container mx-auto text-center">
              <h2 className="text-3xl font-bold mb-12">How It Works</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                  { step: "Connect", desc: "Link accounts + select competitors" },
                  { step: "Analyze", desc: "AI processes competitor data" },
                  { step: "Optimize", desc: "Get actionable insights + generated campaigns" },
                ].map(s => (
                  <Card key={s.step}>
                    <div className="p-6">
                      <h3 className="text-xl font-semibold mb-2">{s.step}</h3>
                      <p className="text-gray-600">{s.desc}</p>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          </section>
        </main>
      </div>
    </Layout>
  );
}
