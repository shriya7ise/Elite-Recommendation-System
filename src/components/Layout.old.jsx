import { useState, useEffect, useRef } from "react";
import { NavLink } from "react-router-dom";
import { Menu } from "lucide-react";
import gsap from "gsap";

const navItem =
  "px-3 py-2 rounded-lg hover:bg-gray-100 transition text-gray-700";

export default function Layout({ title = "AI Marketing", children }) {
  const [open, setOpen] = useState(false);
  const headerRef = useRef();
  const mainRef = useRef();

  useEffect(() => {
    gsap.fromTo(
      headerRef.current,
      { opacity: 0, y: -20 },
      { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }
    );
    gsap.fromTo(
      mainRef.current,
      { opacity: 0, y: 20 },
      { opacity: 1, y: 0, duration: 0.5, delay: 0.2, ease: "power3.out" }
    );
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {/* Header with nav */}
      <header
        ref={headerRef}
        className="sticky top-0 z-20 bg-white/80 backdrop-blur border-b"
      >
        <div className="px-6 py-4 flex items-center justify-between">
          {/* Left: title */}
          <h2 className="text-xl font-extrabold tracking-tight text-blue-600">
            AI Marketing
          </h2>

          {/* Mobile menu button */}
          <button className="md:hidden" onClick={() => setOpen(!open)}>
            <Menu size={24} />
          </button>

          {/* Desktop Nav */}
          <nav className="hidden md:flex gap-2 lg:gap-4">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `${navItem} ${isActive ? "font-semibold text-blue-600 bg-blue-50" : ""}`
              }
            >
              Landing
            </NavLink>
            <NavLink
              to="/campaigns"
              className={({ isActive }) =>
                `${navItem} ${isActive ? "font-semibold text-blue-600 bg-blue-50" : ""}`
              }
            >
              Campaign Hub
            </NavLink>
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                `${navItem} ${isActive ? "font-semibold text-blue-600 bg-blue-50" : ""}`
              }
            >
              Company Dashboard
            </NavLink>
            <NavLink
              to="/competitors"
              className={({ isActive }) =>
                `${navItem} ${isActive ? "font-semibold text-blue-600 bg-blue-50" : ""}`
              }
            >
              Competitor Intel
            </NavLink>
            <NavLink
              to="/insights"
              className={({ isActive }) =>
                `${navItem} ${isActive ? "font-semibold text-blue-600 bg-blue-50" : ""}`
              }
            >
              AI Insights
            </NavLink>
          </nav>
        </div>

        {/* Mobile dropdown nav */}
        {open && (
          <div className="md:hidden bg-white border-t px-6 py-4 space-y-2">
            <NavLink to="/" end className={navItem} onClick={() => setOpen(false)}>
              Landing
            </NavLink>
            <NavLink to="/campaigns" className={navItem} onClick={() => setOpen(false)}>
              Campaign Hub
            </NavLink>
            <NavLink to="/dashboard" className={navItem} onClick={() => setOpen(false)}>
              Company Dashboard
            </NavLink>
            <NavLink to="/competitors" className={navItem} onClick={() => setOpen(false)}>
              Competitor Intel
            </NavLink>
            <NavLink to="/insights" className={navItem} onClick={() => setOpen(false)}>
              AI Insights
            </NavLink>
          </div>
        )}
      </header>

      {/* Main content */}
      <main ref={mainRef} className="flex-1 p-6">
        {children}
      </main>
    </div>
  );
}