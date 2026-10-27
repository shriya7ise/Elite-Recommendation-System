import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { api, getToken, setToken } from "../lib/api";

const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);

export function AuthProvider({ children }) {
  const [state, setState] = useState({ user: null, business: null });
  const [loading, setLoading] = useState(!!getToken());

  const apply = (d) => setState({ user: d.user, business: d.business });
  const refresh = useCallback(async () => {
    try { apply(await api("/me")); } catch { setToken(null); setState({ user: null, business: null }); }
    setLoading(false);
  }, []);
  useEffect(() => { if (getToken()) refresh(); }, [refresh]);

  const start = async (path, body) => {
    const d = await api(path, { method: "POST", body });
    setToken(d.token); apply(d); return d;
  };
  const value = {
    ...state, loading, refresh,
    login: (email, password) => start("/auth/login", { email, password }),
    register: (payload) => start("/auth/register", payload),
    demo: () => start("/auth/demo"),
    logout: () => { setToken(null); setState({ user: null, business: null }); },
  };
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}
