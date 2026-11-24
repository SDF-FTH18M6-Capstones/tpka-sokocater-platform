
import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { createCaterer } from "../../api";
import Input from "../../components/Input";
import Button from "../../components/Button";

function CatererForm() {
  const { user } = useAuth();

  const [formData, setFormData] = useState({
    businessName: "",
    description: "",
    location: "",
    phone: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((previousData) => ({
      ...previousData,
      [name]: value,
    }));
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
      };

      const response = await createCaterer(payload);

      setSuccess(
        response.message || "Your caterer profile was created successfully!"
      );
    } catch (err) {
      setError(
        typeof err.message === "string"
          ? err.message
          : "Unable to create your profile. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-container">
      <h1>Caterer Profile</h1>
      <p>Add your catering business details.</p>

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {success && (
        <p className="success-message" role="status">
          {success}
        </p>
      )}

      <form onSubmit={handleSubmit}>
        <Input
          label="Business Name"
          name="businessName"
          value={formData.businessName}
          onChange={handleChange}
          placeholder="Enter business name"
          required
        />

        <div className="form-group">
          <label htmlFor="description">Business Description</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Describe your catering services"
          />
        </div>

        <Input
          label="Business Location"
          name="location"
          value={formData.location}
          onChange={handleChange}
          placeholder="Enter business location"
          required
        />

        <Input
          label="Phone Number"
          name="phone"
          type="tel"
          value={formData.phone}
          onChange={handleChange}
          placeholder="Enter phone number"
        />

        <Button type="submit" disabled={loading}>
          {loading ? "Saving Profile..." : "Save Caterer Profile"}
        </Button>
      </form>
    </div>
  );
}

export default CatererForm;
