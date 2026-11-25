import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getBookings, getCatererById, deleteBooking } from "../../api";

export default function MyBookings() {
  const [bookings, setBookings] = useState([]);
  const [caterers, setCaterers] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    try {
      setLoading(true);
      const json = await getBookings();
      const list = json.data || json || [];
      setBookings(list);
      const ids = [...new Set(list.map(b => b.caterer_id))];
      const map = {};
      await Promise.all(ids.map(async (id) => {
        try {
          const j = await getCatererById(id);
          const c = j.data || j;
          map[id] = c.business_name || c.company_name || c.name || `Caterer #${id}`;
        } catch { map[id] = `Caterer #${id}`; }
      }));
      setCaterers(map);
    } catch { setError("Failed to load bookings."); }
    finally { setLoading(false); }
  }

  useEffect(() => { load(); }, []);

  async function handleCancel(id) {
    if (!confirm("Cancel this pending booking?")) return;
    try { await deleteBooking(id); load(); }
    catch (e) { alert(e.message); }
  }

  if (loading) return <p>Loading your bookings...</p>;
  if (error) return <p>{error}</p>;
  if (!bookings.length) return <div><h2>My Bookings</h2><p>No bookings yet.</p><Link to="/caterers">Find a caterer</Link></div>;

  return (
    <div>
      <h2>My Bookings</h2>
      {bookings.map(b => (
        <div key={b.id} style={{ border: "1px solid #ddd", padding: 16, marginBottom: 12, borderRadius: 8 }}>
          <h3>{caterers[b.caterer_id] || `Caterer #${b.caterer_id}`}</h3>
          <p><b>Event:</b> {b.event_type} - {b.event_date} {b.event_start_time} to {b.event_end_time}</p>
          <p><b>Location:</b> {b.event_location} | <b>Guests:</b> {b.guest_count}</p>
          <p><b>Total:</b> KES {b.estimated_total}</p>
          <p><b>Status:</b> {b.status}</p>
          {b.status === "pending" && (
            <button onClick={() => handleCancel(b.id)} style={{ background: "#c0392b", color: "white", border: "none", padding: "8px 12px", borderRadius: 6, cursor: "pointer" }}>Cancel Booking</button>
          )}
        </div>
      ))}
    </div>
  );
}