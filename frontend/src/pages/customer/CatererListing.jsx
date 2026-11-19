function CatererListing() {
  return (
    <div className="page-container">
      <h1>Find the Perfect Caterer</h1>
      <p>Explore trusted catering services for your special events.</p>

      <input
        type="text"
        placeholder="Search for caterers..."
      />
      <button>Search</button>

      <h2>Featured Caterers</h2>

      <div className="caterer-list">
        <div className="caterer-card">
          <h3>Elegant Events Catering</h3>
          <p>Professional catering for weddings and private events.</p>
          <button>View Details</button>
        </div>

        <div className="caterer-card">
          <h3>Delicious Moments</h3>
          <p>Quality meals for birthdays and corporate events.</p>
          <button>View Details</button>
        </div>

        <div className="caterer-card">
          <h3>Perfect Plates</h3>
          <p>Fresh food and catering for every occasion.</p>
          <button>View Details</button>
        </div>
      </div>
    </div>
  );
}

export default CatererListing;