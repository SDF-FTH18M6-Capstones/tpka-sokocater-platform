
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <Link to="/" className="brand">
        Soko<span>Cater</span>
      </Link>

      <div className="nav-links">
        <NavLink to="/">Home</NavLink>
        <a href="/#categories">Categories</a>
        <a href="/#about">About</a>
      </div>

      <div className="nav-actions">
        {isAuthenticated ? (
          <>
            <span>
              Welcome, {user?.name || user?.username || "User"}
            </span>

            <button
              onClick={handleLogout}
              className="nav-button"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="provider-link">
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
