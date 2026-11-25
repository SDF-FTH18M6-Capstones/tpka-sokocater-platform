import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { getBookings, updateBooking, getPackages, getMenus, createMenu, getMenuItems, createMenuItem } from "../../api";

const menuItems = ["Overview", "My Packages", "Manage Menus", "My Bookings", "Business Profile"];

function Dashboard() {
  const [activeTab, setActiveTab] = useState("Overview");
  const [bookings, setBookings] = useState([]);
  const [packages, setPackages] = useState([]);
  const [menus, setMenus] = useState([]);
  const [menuItemsList, setMenuItemsList] = useState([]);
  const [menuName, setMenuName] = useState("");
  const [menuDesc, setMenuDesc] = useState("");
  const [selectedMenuId, setSelectedMenuId] = useState("");
  const [itemName, setItemName] = useState("");
  const [itemPrice, setItemPrice] = useState("");
  const [itemDesc, setItemDesc] = useState("");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  async function load() {
    try {
      const b = await getBookings();
      setBookings(b.data || b || []);
      const p = await getPackages();
      const m = await getMenus(); setMenus(m.data || m || []);
      const mi = await getMenuItems(); setMenuItemsList(mi.data || mi || []);
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

  async function handleCreateMenu(e) {
    e.preventDefault();
    try {
      await createMenu({ menu_name: menuName, description: menuDesc });
      setMenuName(""); setMenuDesc(""); load();
    } catch (err) { alert(err.message); }
  }
  async function handleCreateMenuItem(e) {
    e.preventDefault();
    try {
      await createMenuItem({ menu_id: Number(selectedMenuId), item_name: itemName, description: itemDesc, price: Number(itemPrice) });
      setItemName(""); setItemPrice(""); setItemDesc(""); load();
    } catch (err) { alert(err.message); }
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
                        {activeTab === "Manage Menus" && (
              <section className="dashboard-panel">
                <h2>Manage Menus</h2>
                <h3>1. Create Menu</h3>
                <form onSubmit={handleCreateMenu} style={{ display: "flex", flexDirection: "column", gap: 10, maxWidth: 400 }}>
                  <input value={menuName} onChange={e => setMenuName(e.target.value)} placeholder="Menu name e.g. Wedding Menu" required />
                  <input value={menuDesc} onChange={e => setMenuDesc(e.target.value)} placeholder="Description" />
                  <button type="submit" className="save-profile-button">+ Create Menu</button>
                </form>
                <h3 style={{ marginTop: 20 }}>2. Add Menu Item</h3>
                <form onSubmit={handleCreateMenuItem} style={{ display: "flex", flexDirection: "column", gap: 10, maxWidth: 400 }}>
                  <select value={selectedMenuId} onChange={e => setSelectedMenuId(e.target.value)} required>
                    <option value="">Select Menu...</option>
                    {menus.map(m => <option key={m.id} value={m.id}>{m.menu_name}</option>)}
                  </select>
                  <input value={itemName} onChange={e => setItemName(e.target.value)} placeholder="Item name e.g. Pilau" required />
                  <input value={itemPrice} onChange={e => setItemPrice(e.target.value)} placeholder="Price e.g. 500" type="number" required />
                  <input value={itemDesc} onChange={e => setItemDesc(e.target.value)} placeholder="Description" />
                  <button type="submit" className="save-profile-button">+ Add Item</button>
                </form>
                <h3 style={{ marginTop: 20 }}>Your Menus & Items</h3>
                {menus.length === 0 ? <span className="empty-state">No menus yet.</span> : menus.map(m => (
                  <div key={m.id} style={{ border: "1px solid #ddd", padding: 12, borderRadius: 8, marginBottom: 10 }}>
                    <b>{m.menu_name}</b> - {m.description || ""}
                    {menuItemsList.filter(i => i.menu_id === m.id).map(i => <p key={i.id} style={{ marginLeft: 12 }}>• {i.item_name} - KES {i.price} (ID: {i.id})</p>)}
                  </div>
                ))}
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