import { useEffect, useState, useCallback } from "react";
import { ChevronDown, Search, BadgeCheck, Loader2 } from "lucide-react";
import Layout from "../components/Layout";
import { api } from "../lib/api";
import { useAuth } from "../context/AuthContext";

const chip = "inline-block text-xs px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 mr-1 mb-1";
const SRC = { "gemini+serpapi": "AI + web verified", serpapi: "Web (SerpAPI)", gemini: "AI suggested (unverified)", "demo-dataset": "Project dataset", "demo-sample": "Sample data" };

export default function CompetitorIntel() {
  const { business } = useAuth();
  const [comps, setComps] = useState([]);
  const [themes, setThemes] = useState(null);
  const [open, setOpen] = useState(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");

  const load = useCallback(async () => {
    const [c, t] = await Promise.all([api("/competitors"), api("/nlp/themes")]);
    setComps(c.competitors); setThemes(t);
  }, []);
  useEffect(() => { load().catch((e) => setErr(e.message)); }, [load]);

  const discover = async () => {
    setBusy(true); setErr(""); setMsg("");
    try {
      const r = await api("/competitors/discover", { method: "POST" });
      setMsg(`Found ${r.count} competitors and ${r.ads} ads. ${r.notes.join(" ")}`);
      await load();
    } catch (e) { setErr(e.message); } finally { setBusy(false); }
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-2xl font-bold">Competitors of {business?.company}</h1>
            <p className="text-sm text-gray-500">{business?.industry} · Gemini proposes, SerpAPI verifies.</p>
          </div>
          <button onClick={discover} disabled={busy} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg disabled:opacity-60">
            {busy ? <Loader2 className="animate-spin" size={16} /> : <Search size={16} />} Discover competitors
          </button>
        </div>
        {msg && <p className="text-sm bg-green-50 text-green-700 rounded-lg p-3">{msg}</p>}
        {err && <p className="text-sm bg-red-50 text-red-700 rounded-lg p-3">{err}</p>}

        {themes?.themes?.length > 0 && (
          <div className="bg-white border rounded-2xl p-5">
            <h2 className="font-semibold mb-2">Messaging themes across {themes.ads_analyzed} competitor ads</h2>
            <div className="grid sm:grid-cols-2 gap-3">
              {themes.themes.map((t, i) => (
                <div key={i} className="border rounded-xl p-3"><div className="font-medium capitalize">{t.theme} <span className="text-gray-400 text-sm">· {t.size} ads</span></div>
                  <div className="mt-1">{t.terms.slice(0, 5).map((w) => <span key={w} className={chip}>{w}</span>)}</div></div>
              ))}
            </div>
          </div>
        )}

        {comps.length === 0 && !err && <p className="text-gray-500">No competitors yet — click “Discover competitors”.</p>}
        <div className="space-y-3">
          {comps.map((c) => (
            <div key={c.id} className="bg-white border rounded-2xl overflow-hidden">
              <button onClick={() => setOpen(open === c.id ? null : c.id)} className="w-full flex items-center gap-4 p-4 text-left hover:bg-gray-50">
                <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-700 grid place-items-center font-bold">{c.name[0]}</div>
                <div className="flex-1 min-w-0">
                  <div className="font-semibold flex items-center gap-1">{c.name}{c.verified ? <BadgeCheck size={16} className="text-green-600" /> : null}</div>
                  <div className="text-xs text-gray-500">{c.domain || "—"} · {SRC[c.source] || c.source} · {c.ads.length} ads</div>
                </div>
                <div className="hidden sm:block w-28"><div className="text-xs text-gray-500">Threat {c.threat}/10</div>
                  <div className="h-2 bg-gray-100 rounded"><div className="h-2 rounded bg-red-500" style={{ width: `${c.threat * 10}%` }} /></div></div>
                <ChevronDown className={`transition ${open === c.id ? "rotate-180" : ""}`} />
              </button>
              {open === c.id && (
                <div className="border-t p-4 space-y-4 text-sm">
                  {c.positioning && <p><b>Positioning:</b> {c.positioning}</p>}
                  <div className="grid sm:grid-cols-2 gap-3">
                    {c.strengths.length > 0 && <div><b className="text-green-700">Strengths</b><ul className="list-disc ml-5">{c.strengths.map((s) => <li key={s}>{s}</li>)}</ul></div>}
                    {c.weaknesses.length > 0 && <div><b className="text-red-700">Weaknesses</b><ul className="list-disc ml-5">{c.weaknesses.map((s) => <li key={s}>{s}</li>)}</ul></div>}
                  </div>
                  {c.ads.map((a) => (
                    <div key={a.id} className="border rounded-xl p-3">
                      <div className="text-xs text-gray-500">{a.platform} · {a.ad_type} · {a.source}</div>
                      <div className="font-medium">{a.title}</div>
                      <p className="text-gray-600">{a.description}</p>
                      <div className="mt-1">
                        <span className={chip}>{a.analysis.sentiment}</span><span className={chip}>CTA: {a.analysis.cta}</span>
                        <span className={chip}>Urgency: {a.analysis.urgency}</span><span className={chip}>{a.analysis.reading_level} read</span>
                        {a.analysis.triggers?.map((t) => <span key={t} className={chip}>{t.replace("_", " ")}</span>)}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
}
