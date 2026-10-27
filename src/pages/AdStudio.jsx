import { useState } from "react";
import Layout from "../components/Layout";
import { api } from "../lib/api";
import { renderAdCard } from "../lib/adCard";
import { useAuth } from "../context/AuthContext";

const input = "w-full border rounded-lg px-3 py-2";

export default function AdStudio() {
  const { business } = useAuth();
  const [f, setF] = useState({ brief: "", platform: "Meta", tone: "confident, friendly", n: 3 });
  const [out, setOut] = useState(null);
  const [imgs, setImgs] = useState({});
  const [busy, setBusy] = useState("");
  const [err, setErr] = useState("");
  const [note, setNote] = useState("");

  const gen = async () => {
    setBusy("copy"); setErr(""); setNote(""); setOut(null); setImgs({});
    try { setOut(await api("/adgen/copy", { method: "POST", body: { ...f, n: Number(f.n) } })); } catch (e) { setErr(e.message); } finally { setBusy(""); }
  };
  const card = (v, i) => setImgs((m) => ({ ...m, [i]: { src: renderAdCard({ headline: v.headline, text: v.primary_text, cta: v.cta, brand: business?.company, seed: i }), kind: "card" } }));
  const aiImage = async (v, i) => {
    setBusy(`img${i}`); setErr(""); setNote("");
    try {
      const r = await api("/adgen/image", { method: "POST", body: { headline: v.headline, visual_brief: `${v.primary_text} (${v.angle})`, platform: f.platform } });
      setImgs((m) => ({ ...m, [i]: { src: r.image, kind: "ai" } }));
    } catch (e) {
      card(v, i);
      setNote(`AI image unavailable (${e.message.slice(0, 110)}…). Showing a designed ad card instead.`);
    } finally { setBusy(""); }
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-5">
        <h1 className="text-2xl font-bold">Ad Studio <span className="text-sm font-normal text-gray-500">powered by Gemini</span></h1>
        <div className="bg-white border rounded-2xl p-5 space-y-3">
          <textarea className={input} rows={2} placeholder="What are you promoting? e.g. ML Pro Cert, 20% off this month" value={f.brief} onChange={(e) => setF({ ...f, brief: e.target.value })} />
          <div className="grid grid-cols-3 gap-3">
            <select className={input} value={f.platform} onChange={(e) => setF({ ...f, platform: e.target.value })}>{["Meta", "Google", "LinkedIn", "YouTube"].map((p) => <option key={p}>{p}</option>)}</select>
            <input className={input} value={f.tone} onChange={(e) => setF({ ...f, tone: e.target.value })} />
            <input className={input} type="number" min="1" max="5" value={f.n} onChange={(e) => setF({ ...f, n: e.target.value })} />
          </div>
          <button onClick={gen} disabled={f.brief.length < 3 || busy} className="bg-blue-600 text-white px-4 py-2 rounded-lg disabled:opacity-50">{busy === "copy" ? "Generating…" : "Generate ad copy"}</button>
        </div>
        {err && <p className="bg-red-50 text-red-700 rounded-lg p-3 text-sm">{err}</p>}
        {note && <p className="bg-yellow-50 text-yellow-800 rounded-lg p-3 text-sm">{note}</p>}
        {out?.warning && <p className="bg-yellow-50 text-yellow-800 rounded-lg p-3 text-sm">{out.warning}</p>}
        <div className="grid md:grid-cols-3 gap-4">
          {out?.variations.map((v, i) => (
            <div key={i} className="bg-white border rounded-2xl p-4 text-sm space-y-2">
              <div className="text-xs uppercase text-blue-600">{v.angle}</div>
              <div className="font-bold text-base">{v.headline}</div>
              <p className="text-gray-600">{v.primary_text}</p>
              <div className="text-xs text-gray-500">CTA: {v.cta} · {v.audience}</div>
              {imgs[i] ? (<>
                <img src={imgs[i].src} alt={v.headline} className="rounded-lg w-full" />
                <a href={imgs[i].src} download={`ad-${i + 1}.png`} className="block text-center text-blue-700 underline">Download ({imgs[i].kind === "ai" ? "AI image" : "ad card"})</a>
              </>) : (
                <div className="grid grid-cols-2 gap-2">
                  <button onClick={() => card(v, i)} className="border border-blue-200 text-blue-700 rounded-lg py-1.5">Ad card (free)</button>
                  <button onClick={() => aiImage(v, i)} disabled={!!busy} className="border border-blue-200 text-blue-700 rounded-lg py-1.5 disabled:opacity-50">{busy === `img${i}` ? "Creating…" : "AI image"}</button>
                </div>)}
            </div>))}
        </div>
      </div>
    </Layout>
  );
}
