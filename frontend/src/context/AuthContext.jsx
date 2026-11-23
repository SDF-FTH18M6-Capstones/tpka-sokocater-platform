import { createContext, useContext, useState } from "react";

const AuthContext = createContext();

AuthContext.displayName = "AuthContext";

const API_URL = import.meta.env.VITE_API_URL || "/api";

const getMessage = (value) =>
  typeof value === "string" ? value : JSON.stringify(value);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("sokocater_user")) || null;
    } catch {
      return null;
    }
  });

  const [token, setToken] = useState(
    () => localStorage.getItem("sokocater_token")
  );

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const signup = async (formData) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          getMessage(data.message || data.error || "Signup failed")
        );
      }

      const jwt = data.access_token || data.token;
      const userData = data.user || {
        full_name: formData.full_name,
        email: formData.email,
        role: formData.role,
      };

      if (jwt) {
        localStorage.setItem("sokocater_token", jwt);
        localStorage.setItem("sokocater_user", JSON.stringify(userData));
        setToken(jwt);
        setUser(userData);
      }

      return userData;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          getMessage(data.message || data.error || "Login failed")
        );
      }

      const jwt = data.access_token || data.token;
      const userData = data.user || { email };

      if (!jwt) {
        throw new Error("Login response did not include an authentication token");
      }

      localStorage.setItem("sokocater_token", jwt);
      localStorage.setItem("sokocater_user", JSON.stringify(userData));

      setToken(jwt);
      setUser(userData);

      return userData;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("sokocater_token");
    localStorage.removeItem("sokocater_user");

    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: Boolean(user && token),
        loading,
        error,
        signup,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  return useContext(AuthContext);
}
