import { useEffect, useState } from "react";
import { ThumbsUp, ThumbsDown } from "lucide-react";
import Layout from "../components/Layout";
import { api } from "../lib/api";

export default function Insights() {
  const [d, setD] = useState(null);
  const [err, setErr] = useState("");
  useEffect(() => { api("/insights?narrative=true").then(setD).catch((e) => setErr(e.message)); }, []);
  return (
    <Layout>
      <div className="max-w-3xl mx-auto space-y-4">
        <h1 className="text-2xl font-bold">AI Insights</h1>
        {err && <p className="text-red-600">{err}</p>}
        {!d && !err && <p className="text-gray-500">Analyzing…</p>}
        {d?.narrative && <div className="bg-blue-50 border border-blue-100 rounded-2xl p-4 text-sm whitespace-pre-wrap">{d.narrative}</div>}
        {d?.narrative_error && <p className="text-xs text-gray-400">AI summary unavailable: {d.narrative_error}</p>}
        {d?.insights.map((t, i) => {
          const pos = t.startsWith("Positive");
          return <div key={i} className={`flex gap-3 items-start rounded-xl border p-4 ${pos ? "bg-green-50 border-green-100" : "bg-red-50 border-red-100"}`}>
            {pos ? <ThumbsUp className="text-green-600 shrink-0" size={18} /> : <ThumbsDown className="text-red-600 shrink-0" size={18} />}
            <span className="text-sm">{t.replace(/^(Positive|Negative):\s*/, "")}</span></div>;
        })}
      </div>
    </Layout>
  );
}
