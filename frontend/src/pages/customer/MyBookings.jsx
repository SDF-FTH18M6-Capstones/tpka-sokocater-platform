import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getBookings, getCatererById, deleteBooking, createPayment, simulatePayment, createReview } from "../../api";

export default function MyBookings() {
  const [bookings, setBookings] = useState([]);
  const [caterers, setCaterers] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [payingId, setPayingId] = useState(null);
  const [payMethod, setPayMethod] = useState({});
  const [reviewingId, setReviewingId] = useState(null);
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [busy, setBusy] = useState(false);

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

  async function handlePay(b) {
    const method = payMethod[b.id] || "mpesa";
    if (!confirm(`Pay KES ${b.estimated_total} via ${method}?`)) return;
    setPayingId(b.id);
    setBusy(true);
    try {
      // 1. Create payment - backend returns payment with id
      const created = await createPayment(b.id, method);
      const payment = created.data || created;
      // 2. Simulate success - demo only, no real M-Pesa
      await simulatePayment(payment.id, "successful");
      alert("Payment successful!");
      load();
    } catch (e) {
      // 409 = already paid / payment exists, 400 = booking not payable yet
      alert(e.message);
    } finally {
      setPayingId(null);
      setBusy(false);
    }
  }

  async function handleReview(b) {
    if (!rating || rating < 1 || rating > 5) { alert("Rating must be 1-5"); return; }
    setBusy(true);
    try {
      await createReview(b.id, Number(rating), comment);
      alert("Review submitted!");
      setReviewingId(null);
      setComment("");
      setRating(5);
    } catch (e) {
      // 409 = already reviewed, 400 = booking not completed yet
      alert(e.message);
    } finally { setBusy(false); }
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

          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 8 }}>
            {b.status === "pending" && (
              <button onClick={() => handleCancel(b.id)} style={{ background: "#c0392b", color: "white", border: "none", padding: "8px 12px", borderRadius: 6, cursor: "pointer" }}>Cancel Booking</button>
            )}

            {(b.status === "accepted" || b.status === "confirmed") && (
              <>
                <select value={payMethod[b.id] || "mpesa"} onChange={(e) => setPayMethod({ ...payMethod, [b.id]: e.target.value })} style={{ padding: "8px", borderRadius: 6 }}>
                  <option value="mpesa">M-Pesa</option>
                  <option value="card">Card</option>
                  <option value="cash">Cash</option>
                </select>
                <button disabled={busy && payingId === b.id} onClick={() => handlePay(b)} style={{ background: "#27ae60", color: "white", border: "none", padding: "8px 12px", borderRadius: 6, cursor: "pointer" }}>
                  {payingId === b.id ? "Paying..." : "Pay Now"}
                </button>
              </>
            )}

            {b.status === "completed" && reviewingId !== b.id && (
              <button onClick={() => { setReviewingId(b.id); setRating(5); setComment(""); }} style={{ background: "#f39c12", color: "white", border: "none", padding: "8px 12px", borderRadius: 6, cursor: "pointer" }}>Leave Review</button>
            )}
          </div>

          {reviewingId === b.id && (
            <div style={{ marginTop: 12, padding: 12, background: "#f9f9f9", borderRadius: 6 }}>
              <label><b>Rating (1-5):</b> </label>
              <select value={rating} onChange={(e) => setRating(e.target.value)} style={{ padding: "6px", marginLeft: 6 }}>
                <option value={1}>1</option>
                <option value={2}>2</option>
                <option value={3}>3</option>
                <option value={4}>4</option>
                <option value={5}>5</option>
              </select>
              <br />
              <textarea value={comment} onChange={(e) => setComment(e.target.value)} placeholder="How was the food / service? (optional)" rows={3} style={{ width: "100%", marginTop: 8, padding: 8 }} />
              <br />
              <button disabled={busy} onClick={() => handleReview(b)} style={{ background: "#27ae60", color: "white", border: "none", padding: "8px 12px", borderRadius: 6, cursor: "pointer", marginRight: 8 }}>Submit Review</button>
              <button onClick={() => setReviewingId(null)} style={{ padding: "8px 12px", borderRadius: 6, cursor: "pointer" }}>Cancel</button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
