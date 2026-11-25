import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Input from "../../components/Input";
import Button from "../../components/Button";
import { createPackage, getMenuItems, getMenus } from "../../api";

function CreatePackage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    package_name: "",
    description: "",
    price_per_guest: "",
    minimum_guests: "",
    maximum_guests: "",
  });
  const [menuItems, setMenuItems] = useState([]);
  const [selectedItems, setSelectedItems] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    Promise.all([getMenus(), getMenuItems()]).then(([menusRes, itemsRes]) => {
      const menus = menusRes.data || menusRes || [];
      const items = itemsRes.data || itemsRes || [];
      // Only show items from menus YOU own - backend getMenus() already filters to you,
      // so if menus list is yours, this filters out other caterers' items
      const myMenuIds = new Set(menus.map(m => m.id));
      setMenuItems(items.filter(i => myMenuIds.has(i.menu_id)));
    }).catch(() => {});
  }, []);

  function toggleItem(id) {
    setSelectedItems(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  }

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
        menu_item_ids: selectedItems,
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
        
        <div style={{ margin: "16px 0" }}>
          <label style={{ fontWeight: "bold" }}>Select Menu Items (from Manage Menus)</label>
          {menuItems.length === 0 ? (
            <p style={{ color: "#666" }}>No menu items yet. Go to Dashboard -&gt; Manage Menus -&gt; Add Item first.</p>
          ) : (
            menuItems.map(item => (
              <label key={item.id} style={{ display: "flex", gap: 8, alignItems: "center", margin: "6px 0" }}>
                <input type="checkbox" checked={selectedItems.includes(item.id)} onChange={() => toggleItem(item.id)} />
                {item.item_name} - KES {item.price} (ID: {item.id})
              </label>
            ))
          )}
        </div>
        <Button type="submit" disabled={loading}>{loading ? "Creating..." : "Create Package"}</Button>
      </form>
    </div>
  );
}

export default CreatePackage;