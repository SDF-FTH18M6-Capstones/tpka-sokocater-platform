import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <nav className="navbar">
      <Link to="/" className="brand">
        Soko<span>Cater</span>
      </Link>

      <div className="nav-links">
        <NavLink to="/">Home</NavLink>
        <NavLink to="/caterers">Find Catering</NavLink>
        <a href="/#categories">Categories</a>
        <a href="/#about">About</a>
      </div>

      <div className="nav-actions">
        <Link to="/caterer/dashboard" className="provider-link">
          Caterer Portal
        </Link>
        {isAuthenticated ? (
          <>
            <span style={{ fontSize: "14px" }}>{user?.full_name || user?.email}</span>
            <button onClick={handleLogout} className="nav-button">
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="nav-button">
              Login
            </Link>
            <Link to="/signup" className="nav-button">
              Sign Up
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
