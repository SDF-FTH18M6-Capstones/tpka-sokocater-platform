import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

function Signup() {
  const [formData, setFormData] = useState({ name: "", email: "", password: "", confirmPassword: "", role: "customer" });
  const { signup, loading, error } = useAuth();
  const navigate = useNavigate();
  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) { alert("Passwords do not match!"); return; }
    try { await signup(formData.name, formData.email, formData.password, formData.role); navigate("/"); } catch (err) { console.error("Signup failed:", err.message); }
  };
  return (
    <div className="auth-container">
      <h2>Create Your SokoCater Account</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input type="text" name="name" placeholder="Full Name" value={formData.name} onChange={handleChange} required />
        <input type="email" name="email" placeholder="Email Address" value={formData.email} onChange={handleChange} required />
        <input type="password" name="password" placeholder="Password" value={formData.password} onChange={handleChange} required />
        <input type="password" name="confirmPassword" placeholder="Confirm Password" value={formData.confirmPassword} onChange={handleChange} required />
        <select name="role" value={formData.role} onChange={handleChange} required>
          <option value="customer">I want to order food - Customer</option>
          <option value="caterer">I want to sell food - Caterer</option>
        </select>
        <button type="submit" disabled={loading}>{loading ? "Creating..." : "Sign Up"}</button>
      </form>
    </div>
  );
}
export default Signup;
