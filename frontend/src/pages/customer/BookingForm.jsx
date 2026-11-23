
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Input from "../../components/Input";
import Select from "../../components/Select";
import Button from "../../components/Button";
function BookingForm() {
  const location = useLocation();
  const navigate = useNavigate();
  const caterer = location.state?.caterer || { id: 1, name: "Elegant Events Catering", location: "Nairobi" };
  const [formData, setFormData] = useState({ eventType: "Birthday", eventDate: "", guests: "40", location: "Nairobi", packageId: "1" });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  function handleChange(e) { const { name, value } = e.target; setFormData({ ...formData, [name]: value }); }
  async function handleSubmit(e) {
    e.preventDefault(); setLoading(true); setMessage(""); setError("");
    const token = localStorage.getItem("sokocater_token") || localStorage.getItem("token") || localStorage.getItem("access_token");
    if (!token) { setError("You must login as a customer first. No token found."); setLoading(false); return; }
    const payload = { caterer_id: Number(caterer.id), package_id: Number(formData.packageId), event_date: formData.eventDate, event_type: formData.eventType, event_location: formData.location, guest_count: Number(formData.guests) };
    try {
      const res = await fetch("http://127.0.0.1:5000/api/bookings", { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify(payload) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || data.error || `Failed: ${res.status}`);
      setMessage(`Booking created! ID: ${data.data.id}, Total: KES ${data.data.estimated_total}`);
      setTimeout(() => navigate("/customer/dashboard"), 1500);
    } catch (err) { setError(`${err.message}`); } finally { setLoading(false); }
  }
  return (
    <div className="page-container">
      <h1>Book Your Catering Service</h1>
      <p style={{ background: "#f0f7ff", padding: "10px", borderRadius: "8px" }}><strong>Booking for:</strong> {caterer.name} - {caterer.location}</p>
      {message && <p style={{ color: "green", fontWeight: "bold" }}>{message}</p>}
      {error && <p style={{ color: "red", fontWeight: "bold" }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <Select label="Event Type" name="eventType" value={formData.eventType} onChange={handleChange} options={[{value:"Wedding",label:"Wedding"},{value:"Birthday",label:"Birthday"},{value:"Corporate",label:"Corporate Event"},{value:"Private",label:"Private Event"}]} />
        <Input label="Event Date" name="eventDate" type="date" value={formData.eventDate} onChange={handleChange} />
        <Input label="Number of Guests" name="guests" type="number" value={formData.guests} onChange={handleChange} placeholder="40" />
        <Input label="Package ID (for now)" name="packageId" type="number" value={formData.packageId} onChange={handleChange} placeholder="1" />
        <Input label="Event Location" name="location" value={formData.location} onChange={handleChange} placeholder="Nairobi" />
        <Button type="submit" disabled={loading}>{loading ? "Submitting..." : "Submit Booking"}</Button>
      </form>
    </div>
  );
}
export default BookingForm;
