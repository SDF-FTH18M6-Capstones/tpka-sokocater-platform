import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Input from "../../components/Input";
import Button from "../../components/Button";
import { createPackage } from "../../api";

function CreatePackage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    package_name: "",
    description: "",
    price_per_guest: "",
    minimum_guests: "",
    maximum_guests: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const payload = {
        package_name: formData.package_name.trim(),
        description: formData.description.trim() || null,
        price_per_guest: String(formData.price_per_guest),
        minimum_guests: Number(formData.minimum_guests),
        maximum_guests: formData.maximum_guests ? Number(formData.maximum_guests) : null,
        menu_item_ids: [],
        addon_ids: [],
      };
      await createPackage(payload);
      navigate("/caterer/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-container">
      <h1>Create Package</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <Input label="Package Name" name="package_name" value={formData.package_name} onChange={handleChange} placeholder="e.g. Wedding Gold Package" />
        <Input label="Description" name="description" value={formData.description} onChange={handleChange} placeholder="What is included?" />
        <Input label="Price Per Guest (Ksh)" name="price_per_guest" type="number" value={formData.price_per_guest} onChange={handleChange} placeholder="1500" />
        <Input label="Min Guests" name="minimum_guests" type="number" value={formData.minimum_guests} onChange={handleChange} placeholder="50" />
        <Input label="Max Guests (leave empty for no max)" name="maximum_guests" type="number" value={formData.maximum_guests} onChange={handleChange} placeholder="500" />
        <Button type="submit" disabled={loading}>{loading ? "Creating..." : "Create Package"}</Button>
      </form>
    </div>
  );
}

export default CreatePackage;