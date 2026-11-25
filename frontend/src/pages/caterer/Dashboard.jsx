import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { getBookings, updateBooking, getPackages } from "../../api";

const menuItems = ["Overview", "My Packages", "My Bookings", "Business Profile"];

function Dashboard() {
  const [activeTab, setActiveTab] = useState("Overview");
  const [bookings, setBookings] = useState([]);
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  async function load() {
    try {
      const b = await getBookings();
      setBookings(b.data || b || []);
      const p = await getPackages();
      setPackages(p.data || p || []);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }

  useEffect(() => { load(); }, []);

  async function handleStatus(id, status) {
    try { await updateBooking(id, status); load(); }
    catch (e) { alert(e.message); }
  }

  const total = bookings.length;
  const pending = bookings.filter(b => b.status === "pending").length;
  const accepted = bookings.filter(b => ["accepted", "confirmed"].includes(b.status)).length;

  function renderBookings(list) {
    if (!list.length) return <span className="empty-state">No bookings yet.</span>;
    return list.map(b => (
      <div key={b.id} style={{ border: "1px solid #ddd", padding: 14, marginBottom: 10, borderRadius: 8 }}>
        <p><b>Booking #{b.id}</b> - {b.event_type} on {b.event_date} | {b.guest_count} guests | KES {b.estimated_total}</p>
        <p>Location: {b.event_location} | Status: <b>{b.status}</b></p>
        {b.status === "pending" && (
          <>
            <button onClick={() => handleStatus(b.id, "accepted")} style={{ background: "#0a7a42", color: "white", border: "none", padding: "8px 12px", borderRadius: 6, marginRight: 8, cursor: "pointer" }}>Accept</button>
            <button onClick={() => handleStatus(b.id, "rejected")} style={{ background: "#c0392b", color: "white", border: "none", padding: "8px 12px", borderRadius: 6, cursor: "pointer" }}>Reject</button>
          </>
        )}
        {b.status === "accepted" && (
          <button onClick={() => handleStatus(b.id, "confirmed")} style={{ background: "#0a7a42", color: "white", border: "none", padding: "8px 12px", borderRadius: 6, cursor: "pointer" }}>Confirm</button>
        )}
        {b.status === "confirmed" && (
          <button onClick={() => handleStatus(b.id, "completed")} style={{ background: "#0a7a42", color: "white", border: "none", padding: "8px 12px", borderRadius: 6, cursor: "pointer" }}>Mark Completed</button>
        )}
      </div>
    ));
  }

  return (
    <main className="dashboard">
      <aside className="sidebar">
        <h2>Provider Portal</h2>
        <nav>
          {menuItems.map(item => (
            <button key={item} type="button" className={activeTab === item ? "active" : ""} onClick={() => setActiveTab(item)}>{item}</button>
          ))}
        </nav>
      </aside>
      <section className="dashboard-content">
        <div className="dashboard-header">
          <div><span className="eyebrow">CATERER MANAGEMENT</span><h1>{activeTab}</h1></div>
        </div>
        {loading ? <p>Loading...</p> : (
          <>
            {activeTab === "Overview" && (
              <>
                <div className="stats-grid">
                  <article className="stat-card"><span>📅</span><h3>{total}</h3><p>Total Bookings</p></article>
                  <article className="stat-card"><span>⏳</span><h3>{pending}</h3><p>Pending Requests</p></article>
                  <article className="stat-card"><span>🍽️</span><h3>{accepted}</h3><p>Active Services</p></article>
                  <article className="stat-card"><span>📦</span><h3>{packages.length}</h3><p>My Packages</p></article>
                </div>
                <section className="dashboard-panel"><h2>Recent Bookings</h2>{renderBookings(bookings.slice(0, 5))}</section>
              </>
            )}
            {activeTab === "My Packages" && (
              <section className="dashboard-panel">
                <h2>My Packages</h2>
                <Link to="/caterer/create-package"><button type="button" className="save-profile-button">+ Create New Package</button></Link><br /><br />
                {packages.length === 0 ? <span className="empty-state">No packages yet.</span> : packages.map(p => <p key={p.id}>{p.package_name} - KES {p.price_per_guest}/guest ({p.minimum_guests}-{p.maximum_guests || "∞"})</p>)}
              </section>
            )}
            {activeTab === "My Bookings" && (
              <section className="dashboard-panel"><h2>My Bookings</h2>{renderBookings(bookings)}</section>
            )}
            {activeTab === "Business Profile" && (
              <section className="dashboard-panel"><h2>My Business Profile</h2><button type="button" className="save-profile-button" onClick={() => navigate("/caterer/profile")}>Edit Business Profile</button></section>
            )}
          </>
        )}
      </section>
    </main>
  );
}

export default Dashboard;