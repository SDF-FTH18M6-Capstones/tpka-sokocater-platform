import { useState } from "react";
import Input from "../../components/Input";
import Button from "../../components/Button";

function CreatePackage() {
  const [formData, setFormData] = useState({
    name: "",
    price_per_guest: "",
    min_guests: "",
    max_guests: "",
    menus: [],
  });

  const menuOptions = ["Pilau", "Chapati + Beef Stew", "Nyama Choma", "Fried Rice", "Mokimo", "Samosa Platter"];

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  }

  function toggleMenu(item) {
    setFormData((prev) => ({
      ...prev,
      menus: prev.menus.includes(item)
        ? prev.menus.filter((m) => m !== item)
        : [...prev.menus, item],
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    console.log("Package:", formData);
    alert("Package created! Connect to POST /api/packages next");
  }

  return (
    <div className="page-container">
      <h1>Create Package</h1>
      <form onSubmit={handleSubmit}>
        <Input label="Package Name" name="name" value={formData.name} onChange={handleChange} placeholder="e.g. Wedding Gold Package" />
        <Input label="Price Per Guest (Ksh)" name="price_per_guest" type="number" value={formData.price_per_guest} onChange={handleChange} placeholder="1500" />
        <Input label="Min Guests" name="min_guests" type="number" value={formData.min_guests} onChange={handleChange} placeholder="50" />
        <Input label="Max Guests" name="max_guests" type="number" value={formData.max_guests} onChange={handleChange} placeholder="500" />
        <div className="form-group">
          <label>Pick Menus</label>
          {menuOptions.map((item) => (
            <label key={item} style={{ display: "block" }}>
              <input type="checkbox" checked={formData.menus.includes(item)} onChange={() => toggleMenu(item)} /> {item}
            </label>
          ))}
        </div>
        <Button type="submit">Create Package</Button>
      </form>
    </div>
  );
}

export default CreatePackage;
