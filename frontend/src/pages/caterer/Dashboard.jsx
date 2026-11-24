
import { useState } from "react";

const stats = [
  { label: "Total Bookings", value: "0", icon: "📅" },
  { label: "Pending Requests", value: "0", icon: "⏳" },
  { label: "Active Services", value: "0", icon: "🍽️" },
  { label: "Customer Enquiries", value: "0", icon: "💬" },
];

const menuItems = [
  "Overview",
  "My Menus",
  "My Packages",
  "My Bookings",
  "Business Profile",
];

function Dashboard() {
  const [activeTab, setActiveTab] = useState("Overview");
  const [profile, setProfile] = useState({
    businessName: "",
    email: "",
    phone: "",
    location: "",
    description: "",
  });
  const [saved, setSaved] = useState(false);

  function handleProfileChange(event) {
    const { name, value } = event.target;

    setProfile((previous) => ({
      ...previous,
      [name]: value,
    }));

    setSaved(false);
  }

  function handleProfileSubmit(event) {
    event.preventDefault();
    setSaved(true);
  }

  function renderContent() {
    switch (activeTab) {
      case "Overview":
        return (
          <>
            <div className="stats-grid">
              {stats.map((stat) => (
                <article className="stat-card" key={stat.label}>
                  <span>{stat.icon}</span>
                  <h3>{stat.value}</h3>
                  <p>{stat.label}</p>
                </article>
              ))}
            </div>

            <section className="dashboard-panel">
              <h2>Recent Bookings</h2>
              <p>
                Your booking requests will appear here when
                customers start making bookings.
              </p>
              <span className="empty-state">No bookings yet.</span>
            </section>
          </>
        );

            case "My Menus":
        return (
          <section className="dashboard-panel">
            <h2>My Menus</h2>
            <p>Your menu items - Pilau, Chapati, Nyama Choma, etc.</p>
            <span className="empty-state">No menus added yet. Add them in Create Package.</span>
          </section>
        );

      case "My Packages":
        return (
          <section className="dashboard-panel">
            <h2>My Packages</h2>
            <p>All your packages with price per guest.</p>
            <a href="/caterer/create-package"><button type="button" className="save-profile-button">+ Create New Package</button></a>
            <br /><br />
            <span className="empty-state">No packages yet.</span>
          </section>
        );

      case "My Bookings":
        return (
          <section className="dashboard-panel">
            <h2>My Bookings</h2>
            <p>Manage and track your customer booking requests.</p>
            <span className="empty-state">No bookings available yet.</span>
          </section>
        );

      

      case "Enquiries":
        return (
          <section className="dashboard-panel">
            <h2>Customer Enquiries</h2>
            <p>
              View and respond to questions from customers
              interested in your catering services.
            </p>
            <span className="empty-state">No enquiries yet.</span>
          </section>
        );

      case "Business Profile":
        return (
          <section className="dashboard-panel profile-panel">
            <h2>My Business Profile</h2>
            <p>Update your catering business information.</p>

            <form
              className="business-profile-form"
              onSubmit={handleProfileSubmit}
            >
              <div className="profile-form-group">
                <label htmlFor="businessName">Business Name</label>
                <input
                  id="businessName"
                  name="businessName"
                  value={profile.businessName}
                  onChange={handleProfileChange}
                  placeholder="Enter your business name"
                  required
                />
              </div>

              <div className="profile-form-group">
                <label htmlFor="email">Business Email</label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={profile.email}
                  onChange={handleProfileChange}
                  placeholder="Enter your business email"
                  required
                />
              </div>

              <div className="profile-form-group">
                <label htmlFor="phone">Contact Number</label>
                <input
                  id="phone"
                  name="phone"
                  type="tel"
                  value={profile.phone}
                  onChange={handleProfileChange}
                  placeholder="Enter your contact number"
                  required
                />
              </div>

              <div className="profile-form-group">
                <label htmlFor="location">Business Location</label>
                <input
                  id="location"
                  name="location"
                  value={profile.location}
                  onChange={handleProfileChange}
                  placeholder="Enter your business location"
                  required
                />
              </div>

              <div className="profile-form-group">
                <label htmlFor="description">
                  Business Description
                </label>
                <textarea
                  id="description"
                  name="description"
                  value={profile.description}
                  onChange={handleProfileChange}
                  placeholder="Describe your catering business and services"
                  rows="5"
                  required
                />
              </div>

              <button type="submit" className="save-profile-button">
                Save Business Profile
              </button>

              {saved && (
                <p className="profile-success">
                  Profile saved for this session!
                </p>
              )}
            </form>
          </section>
        );

      default:
        return null;
    }
  }

  return (
    <main className="dashboard">
      <aside className="sidebar">
        <h2>Provider Portal</h2>

        <nav>
          {menuItems.map((item) => (
            <button
              key={item}
              type="button"
              className={activeTab === item ? "active" : ""}
              onClick={() => setActiveTab(item)}
            >
              {item}
            </button>
          ))}
        </nav>
      </aside>

      <section className="dashboard-content">
        <div className="dashboard-header">
          <div>
            <span className="eyebrow">CATERER MANAGEMENT</span>
            <h1>
              {activeTab === "Overview"
                ? "Welcome to Your Dashboard"
                : activeTab}
            </h1>
            <p>Manage your catering business from one place.</p>
          </div>
        </div>

        {renderContent()}
      </section>
    </main>
  );
}

export default Dashboard;
