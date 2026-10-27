import { useState, useEffect, useRef } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { Menu, LogOut } from "lucide-react";
import gsap from "gsap";
import { useAuth } from "../context/AuthContext";

const LINKS = [
  ["/dashboard", "Dashboard"], ["/competitors", "Competitors"], ["/recommendations", "Recommendations"],
  ["/studio", "Ad Studio"], ["/insights", "AI Insights"], ["/campaigns", "Campaign Hub"], ["/competitors/ads", "Ad Explorer"],
];
const cls = ({ isActive }) => `px-3 py-2 rounded-lg hover:bg-gray-100 transition text-gray-700 text-sm ${isActive ? "font-semibold text-blue-600 bg-blue-50" : ""}`;

export default function Layout({ children }) {
  const [open, setOpen] = useState(false);
  const { user, business, logout } = useAuth();
  const nav = useNavigate();
  const header = useRef(), main = useRef();

  useEffect(() => {
    gsap.fromTo(header.current, { opacity: 0, y: -20 }, { opacity: 1, y: 0, duration: 0.5 });
    gsap.fromTo(main.current, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5, delay: 0.1 });
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <header ref={header} className="sticky top-0 z-20 bg-white/80 backdrop-blur border-b">
        <div className="px-6 py-3 flex items-center justify-between gap-4">
          <h2 className="text-xl font-extrabold text-blue-600 shrink-0">AI Marketing</h2>
          <nav className="hidden lg:flex gap-1">{LINKS.map(([to, label]) => <NavLink key={to} to={to} end className={cls}>{label}</NavLink>)}</nav>
          <div className="flex items-center gap-3">
            {user && <div className="hidden sm:block text-right leading-tight"><div className="text-sm font-medium">{user.name}</div>
              <div className="text-xs text-gray-500">{business?.company}{user.is_demo ? " · demo" : ""}</div></div>}
            <button title="Log out" onClick={() => { logout(); nav("/login"); }} className="p-2 rounded-lg hover:bg-gray-100"><LogOut size={18} /></button>
            <button className="lg:hidden" onClick={() => setOpen(!open)}><Menu size={24} /></button>
          </div>
        </div>
        {open && <div className="lg:hidden bg-white border-t px-6 py-3 flex flex-col">{LINKS.map(([to, label]) => <NavLink key={to} to={to} end className={cls} onClick={() => setOpen(false)}>{label}</NavLink>)}</div>}
      </header>
      <main ref={main} className="flex-1 p-6">{children}</main>
    </div>
  );
}
