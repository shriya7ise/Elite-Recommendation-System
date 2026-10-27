import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const input = "w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500";
const Field = ({ label, children }) => (
  <label className="block text-sm font-medium text-gray-700">{label}<div className="mt-1">{children}</div></label>
);

export default function Login() {
  const { login, register, demo } = useAuth();
  const nav = useNavigate();
  const [mode, setMode] = useState("login");
  const [step, setStep] = useState(1);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [f, setF] = useState({ name: "", email: "", password: "", role_title: "", company: "", website: "", industry: "", description: "", offerings: "", audience: "", geo: "", monthly_budget: 30000 });
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const run = async (fn) => {
    setBusy(true); setErr("");
    try { await fn(); nav("/dashboard"); } catch (e) { setErr(e.message); } finally { setBusy(false); }
  };
  const canNext = step === 1 ? f.name && /\S+@\S+\.\S+/.test(f.email) && f.password.length >= 8 : step === 2 ? f.company && f.industry : f.description;
  const submit = (e) => {
    e.preventDefault();
    if (mode === "login") return run(() => login(f.email, f.password));
    if (step < 3) return setStep(step + 1);
    run(() => register({ ...f, monthly_budget: Number(f.monthly_budget) || 0, offerings: f.offerings.split(",").map((s) => s.trim()).filter(Boolean) }));
  };

  return (
    <div className="min-h-screen grid place-items-center bg-gradient-to-br from-blue-50 to-white p-4">
      <form onSubmit={submit} className="w-full max-w-md bg-white rounded-2xl shadow-lg border p-8 space-y-4">
        <h1 className="text-2xl font-extrabold text-blue-600">AI Marketing</h1>
        <p className="text-sm text-gray-500">{mode === "login" ? "Sign in to your workspace" : `Create your workspace — step ${step} of 3`}</p>

        {mode === "login" && (<>
          <Field label="Email"><input className={input} type="email" value={f.email} onChange={set("email")} required /></Field>
          <Field label="Password"><input className={input} type="password" value={f.password} onChange={set("password")} required /></Field>
        </>)}

        {mode === "register" && step === 1 && (<>
          <Field label="Your name"><input className={input} value={f.name} onChange={set("name")} /></Field>
          <Field label="Work email"><input className={input} type="email" value={f.email} onChange={set("email")} /></Field>
          <Field label="Password (min 8 chars)"><input className={input} type="password" value={f.password} onChange={set("password")} /></Field>
          <Field label="Your role"><input className={input} placeholder="Head of Growth" value={f.role_title} onChange={set("role_title")} /></Field>
        </>)}
        {mode === "register" && step === 2 && (<>
          <Field label="Company name"><input className={input} value={f.company} onChange={set("company")} /></Field>
          <Field label="Website"><input className={input} placeholder="https://yourcompany.com" value={f.website} onChange={set("website")} /></Field>
          <Field label="Industry"><input className={input} placeholder="Ed-tech, SaaS, Sports nutrition…" value={f.industry} onChange={set("industry")} /></Field>
        </>)}
        {mode === "register" && step === 3 && (<>
          <Field label="What does your business do?"><textarea className={input} rows={3} value={f.description} onChange={set("description")} /></Field>
          <Field label="Products / courses (comma separated)"><input className={input} placeholder="Course A, Course B" value={f.offerings} onChange={set("offerings")} /></Field>
          <Field label="Target audience"><input className={input} value={f.audience} onChange={set("audience")} /></Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Region"><input className={input} value={f.geo} onChange={set("geo")} /></Field>
            <Field label="Monthly ad budget"><input className={input} type="number" min="0" value={f.monthly_budget} onChange={set("monthly_budget")} /></Field>
          </div>
        </>)}

        {err && <p className="text-sm text-red-600 bg-red-50 rounded-lg p-2">{err}</p>}
        <div className="flex gap-2">
          {mode === "register" && step > 1 && <button type="button" onClick={() => setStep(step - 1)} className="px-4 py-2 rounded-lg border">Back</button>}
          <button disabled={busy || (mode === "register" && !canNext)} className="flex-1 bg-blue-600 text-white rounded-lg py-2 font-semibold disabled:opacity-50">
            {busy ? "Please wait…" : mode === "login" ? "Sign in" : step < 3 ? "Continue" : "Create workspace"}
          </button>
        </div>
        <button type="button" onClick={() => run(demo)} disabled={busy} className="w-full border border-blue-200 text-blue-700 rounded-lg py-2 text-sm hover:bg-blue-50">
          Try demo — ed-tech course business
        </button>
        <p className="text-sm text-center text-gray-500">
          {mode === "login" ? "New here?" : "Have an account?"}{" "}
          <button type="button" className="text-blue-600 font-medium" onClick={() => { setMode(mode === "login" ? "register" : "login"); setStep(1); setErr(""); }}>
            {mode === "login" ? "Create an account" : "Sign in"}
          </button>
        </p>
      </form>
    </div>
  );
}
