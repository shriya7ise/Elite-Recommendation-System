
import { useRef, useEffect } from "react";
import gsap from "gsap";

export function Card({ className = "", children }) {
  const cardRef = useRef();

  useEffect(() => {
    gsap.fromTo(
      cardRef.current,
      { opacity: 0, scale: 0.95 },
      { opacity: 1, scale: 1, duration: 0.4, ease: "power2.out" }
    );
  }, []);

  return <div ref={cardRef} className={`bg-white rounded-2xl shadow-sm border p-5 ${className}`}>{children}</div>;
}

export function CardContent({ className = "", children }) {
  const contentRef = useRef();

  useEffect(() => {
    gsap.fromTo(
      contentRef.current,
      { opacity: 0, y: 10 },
      { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }
    );
  }, []);

  return <div ref={contentRef} className={`p-4 ${className}`}>{children}</div>;
}

export function Stat({ label, value, sub }) {
  const statRef = useRef();

  useEffect(() => {
    gsap.fromTo(
      statRef.current,
      { opacity: 0, y: 20 },
      { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }
    );
  }, []);

  return (
    <div ref={statRef} className="bg-white rounded-2xl shadow-sm border p-5">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="text-2xl font-bold mt-1">{value}</div>
      {sub && <div className="text-xs mt-2 text-gray-500">{sub}</div>}
    </div>
  );
}

export function Button({ className = "", children, onClick }) {
  const buttonRef = useRef();

  useEffect(() => {
    gsap.fromTo(
      buttonRef.current,
      { opacity: 0, scale: 0.95 },
      { opacity: 1, scale: 1, duration: 0.4, ease: "power2.out" }
    );
  }, []);

  return (
    <button ref={buttonRef} className={`px-4 py-2 bg-blue-500 text-white rounded ${className}`} onClick={onClick}>
      {children}
    </button>
  );
}

export function Pill({ children }) {
  return <span className="px-2 py-0.5 rounded-full text-xs bg-gray-100">{children}</span>;
}
