import { createContext, useContext, useState } from "react";
const AuthContext = createContext();
export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("sokocater_user");
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem("sokocater_token"));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api";
  const _msg = (v) => typeof v === "string" ? v : JSON.stringify(v);
  const login = async (email, password) => {
    setLoading(true); setError(null);
    try {
      const res = await fetch(`${API_URL}/auth/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) });
      const data = await res.json();
      if (!res.ok) throw new Error(_msg(data.message || data.error || "Login failed"));
      const jwt = data.access_token || data.token;
      const userData = data.user || { email };
      localStorage.setItem("sokocater_token", jwt);
      localStorage.setItem("sokocater_user", JSON.stringify(userData));
      setToken(jwt); setUser(userData); return userData;
    } catch (err) { setError(err.message); throw err; } finally { setLoading(false); }
  };
  const signup = async (name, email, password, role = "customer") => {
    setLoading(true); setError(null);
    try {
      const res = await fetch(`${API_URL}/auth/register`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ full_name: name, email, password, role }) });
      const data = await res.json();
      if (!res.ok) throw new Error(_msg(data.message || data.error || "Signup failed"));
      const jwt = data.access_token || data.token;
      const userData = data.user || { full_name: name, email, role };
      if (jwt) { localStorage.setItem("sokocater_token", jwt); localStorage.setItem("sokocater_user", JSON.stringify(userData)); setToken(jwt); setUser(userData); }
      return userData;
    } catch (err) { setError(err.message); throw err; } finally { setLoading(false); }
  };
  const logout = () => { localStorage.removeItem("sokocater_token"); localStorage.removeItem("sokocater_user"); setToken(null); setUser(null); };
  return <AuthContext.Provider value={{ user, token, isAuthenticated: Boolean(user && token), login, signup, logout, loading, error }}>{children}</AuthContext.Provider>;
}
// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() { return useContext(AuthContext); }
