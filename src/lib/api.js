const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
export const getToken = () => localStorage.getItem("elite_token");
export const setToken = (t) => (t ? localStorage.setItem("elite_token", t) : localStorage.removeItem("elite_token"));

export async function api(path, { method = "GET", body } = {}) {
  const token = getToken();
  const res = await fetch(BASE + path, {
    method,
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (res.status === 401 && token) {
    setToken(null);
    window.location.href = "/login";
  }
  if (!res.ok) {
    const d = data.detail;
    throw new Error(typeof d === "string" ? d : d?.[0]?.msg || `Request failed (${res.status})`);
  }
  return data;
}
