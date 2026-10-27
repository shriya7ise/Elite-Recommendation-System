import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { api } from "../lib/api";

const Box = ({ title, children }) => <section className="bg-white border rounded-2xl p-5"><h2 className="font-semibold mb-3">{title}</h2>{children}</section>;
const badge = { Scale: "bg-green-100 text-green-700", Maintain: "bg-blue-100 text-blue-700", "Test small": "bg-yellow-100 text-yellow-700" };

export default function Recommendations() {
  const [d, setD] = useState(null);
  const [err, setErr] = useState("");
  const [text, setText] = useState("");
  const [res, setRes] = useState(null);
  useEffect(() => { api("/recommendations").then(setD).catch((e) => setErr(e.message)); }, []);
  const analyze = async () => { try { setRes(await api("/nlp/analyze", { method: "POST", body: { text } })); } catch (e) { setErr(e.message); } };

  return (
    <Layout>
      <div className="max-w-5xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold">Recommendations</h1>
        {err && <p className="bg-red-50 text-red-700 rounded-lg p-3 text-sm">{err}</p>}
        {d?.notice && <p className="bg-yellow-50 text-yellow-800 rounded-lg p-3 text-sm">{d.notice}</p>}
        {d && (<>
          <Box title="Where to put your budget">
            <div className="space-y-3">{d.platforms.map((p) => (
              <div key={p.platform} className="border rounded-xl p-3">
                <div className="flex items-center justify-between"><b>{p.platform}</b>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${badge[p.action]}`}>{p.action}</span></div>
                <div className="h-2 bg-gray-100 rounded my-2"><div className="h-2 rounded bg-blue-600" style={{ width: `${Math.min(100, p.score * 100)}%` }} /></div>
                <div className="text-sm text-gray-600">Suggested budget: <b>{p.suggested_budget.toLocaleString()}</b> · confidence: {p.confidence}</div>
                <ul className="text-xs text-gray-500 list-disc ml-5">{p.reasons.map((r) => <li key={r}>{r}</li>)}</ul>
              </div>))}</div>
          </Box>
          <Box title="Messaging angles to test">
            <div className="grid sm:grid-cols-2 gap-3">{d.angles.map((a) => (
              <div key={a.trigger} className="border rounded-xl p-3 text-sm"><b>{a.recommendation}</b>
                <div className="text-xs uppercase text-blue-600">{a.type}</div><p className="text-gray-600">{a.why}</p></div>))}</div>
          </Box>
          <Box title="Campaign actions">
            <table className="w-full text-sm"><tbody>{d.campaign_actions.map((c) => (
              <tr key={c.campaign} className="border-t"><td className="py-2 font-medium">{c.campaign}<div className="text-xs text-gray-500">{c.platform}</div></td>
                <td>{c.action}<div className="text-xs text-gray-500">{c.why}</div></td>
                <td className="text-xs text-orange-600">{c.copy_tips.join("; ")}</td></tr>))}</tbody></table>
          </Box>
          {d.similar_ads.length > 0 && <Box title="Closest competitor ads (semantic match)">
            {d.similar_ads.map((s) => (<div key={s.campaign} className="text-sm mb-2"><b>{s.campaign}</b>
              <ul className="list-disc ml-5 text-gray-600">{s.closest_competitor_ads.map((a, i) => <li key={i}>{a.title} <span className="text-gray-400">({a.competitor}, {a.similarity})</span></li>)}</ul></div>))}
          </Box>}
        </>)}
        <Box title="Ad copy analyzer (NLP)">
          <textarea value={text} onChange={(e) => setText(e.target.value)} rows={3} placeholder="Paste any ad copy…" className="w-full border rounded-lg p-2" />
          <button onClick={analyze} disabled={!text.trim()} className="mt-2 bg-blue-600 text-white px-4 py-2 rounded-lg disabled:opacity-50">Analyze</button>
          {res && <div className="mt-3 text-sm grid grid-cols-2 sm:grid-cols-4 gap-2">
            {[["Sentiment", `${res.sentiment} (${res.sentiment_score})`], ["CTA", res.cta], ["Urgency", res.urgency], ["Reading", `${res.reading_level} (${res.reading_ease})`], ["Triggers", res.triggers.join(", ") || "none"], ["Keywords", res.keywords.join(", ")]]
              .map(([k, v]) => <div key={k} className="border rounded-lg p-2"><div className="text-xs text-gray-500">{k}</div>{v}</div>)}</div>}
        </Box>
      </div>
    </Layout>
  );
}
