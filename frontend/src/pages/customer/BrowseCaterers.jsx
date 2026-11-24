import { useEffect, useState } from "react";
import { getCaterers } from "../../api";
import CatererCard from "../../components/CatererCard";

function BrowseCaterers() {
  const [caterers, setCaterers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadCaterers() {
      try {
        const response = await getCaterers();
        setCaterers(response.data || []);
      } catch (err) {
        setError(err.message || "Unable to load caterers.");
      } finally {
        setLoading(false);
      }
    }

    loadCaterers();
  }, []);

  return (
    <main className="listing-page">
      <section className="listing-hero">
        <span className="eyebrow">SOKOCATER MARKETPLACE</span>
        <h1>Find Your Perfect Caterer</h1>
        <p>
          Explore catering businesses and discover packages
          for your next event.
        </p>
      </section>

      <section className="listing-content">
        <div className="listing-heading">
          <div>
            <span className="eyebrow">OUR CATERERS</span>
            <h2>Available Catering Services</h2>
          </div>
        </div>

        {loading && <p>Loading caterers...</p>}

        {error && (
          <div className="empty-listing">
            <h3>Unable to load caterers</h3>
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && caterers.length === 0 && (
          <div className="empty-listing">
            <h3>No caterers available yet</h3>
            <p>Please check again later.</p>
          </div>
        )}

        {!loading && !error && caterers.length > 0 && (
          <div className="caterer-list">
            {caterers.map((caterer) => (
              <CatererCard key={caterer.id} caterer={caterer} />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

export default BrowseCaterers;