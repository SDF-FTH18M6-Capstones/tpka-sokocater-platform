import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { getCaterers, createCaterer, updateCaterer } from "../../api"
import Input from "../../components/Input";
import Button from "../../components/Button";

function CatererForm() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    businessName: "",
    description: "",
    location: "",
    phone: "",
    category: "",
  });

  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [hasProfile, setHasProfile] = useState(false);

  useEffect(() => {
    async function loadExisting() {
      if (!user?.id) {
        setChecking(false);
        return;
      }
      try {
        const list = await getCaterers();
        const caterers = Array.isArray(list) ? list : list.caterers || list.data || [];
        const mine = caterers.find(
          (c) => c.user_id === user.id || c.userId === user.id
        );
        if (mine) {
          setHasProfile(true);
          setFormData({
            businessName: mine.business_name || mine.businessName || "",
            description: mine.description || "",
            location: mine.location || "",
            phone: mine.contact_number || mine.phone || "",
            category: mine.category || "",
          });
        }
      } catch (e) {
      } finally {
        setChecking(false);
      }
    }
    loadExisting();
  }, [user?.id]);

  function handleChange(event) {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (!user || user.role !== "caterer") {
      setError("Please log in using a caterer account.");
      return;
    }
    if (!user.id) {
      setError("Your account ID could not be found. Please log in again.");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        user_id: user.id,
        business_name: formData.businessName.trim(),
        description: formData.description.trim(),
        location: formData.location.trim(),
        contact_number: formData.phone.trim(),
        category: formData.category,
      };
      let response;
        if (existingProfile?.id) {
         response = await updateCaterer(existingProfile.id, payload);
        } else {  
           response = await createCaterer(payload);
          }
      setSuccess(response.message || "Your caterer profile was created successfully!");
      setTimeout(() => navigate("/caterer/dashboard"), 800);
    } catch (err) {
      setError(typeof err.message === "string" ? err.message : "Unable to create your profile. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  if (checking) return <div className="page-container"><p>Loading your profile...</p></div>;

  return (
    <div className="page-container">
      <h1>{hasProfile ? "Edit Your Business Profile" : "Caterer Profile"}</h1>
      <p>{hasProfile ? "Your saved profile is loaded below." : "Add your catering business details."}</p>
      {error && <p className="error-message" role="alert">{error}</p>}
      {success && <p className="success-message" role="status">{success}</p>}
      <form onSubmit={handleSubmit}>
        <Input label="Business Name" name="businessName" value={formData.businessName} onChange={handleChange} placeholder="Enter business name" required />
        <div className="form-group">
          <label htmlFor="description">Business Description</label>
          <textarea id="description" name="description" value={formData.description} onChange={handleChange} placeholder="Describe your catering services" />
        </div>
        <Input label="Business Location" name="location" value={formData.location} onChange={handleChange} placeholder="Enter business location" required />
        <Input label="Phone Number" name="phone" type="tel" value={formData.phone} onChange={handleChange} placeholder="Enter phone number" />
          <div className="form-group">
            <label htmlFor="category">Category</label>
            <select id="category" name="category" value={formData.category} onChange={handleChange} required>
             <option value="">Select category</option>
             <option value="Wedding">Wedding</option>
             <option value="Corporate">Corporate</option>
             <option value="Birthday">Birthday</option>
             <option value="General">General</option>
            </select>
         </div>
        <Button type="submit" disabled={loading}>
          {loading ? "Saving Profile..." : hasProfile ? "Update Profile" : "Save Caterer Profile"}
        </Button>
      </form>
    </div>
  );
}

export default CatererForm;