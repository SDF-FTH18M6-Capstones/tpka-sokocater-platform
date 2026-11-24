import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getCatererById } from "../../api";

function CatererDetail() {
  const { id } = useParams();

  const [caterer, setCaterer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadCaterer() {
      try {
        setLoading(true);
        setError("");

        const response = await getCatererById(id);
        setCaterer(response.data);
      } catch (err) {
        setError(err.message || "Unable to load caterer.");
      } finally {
        setLoading(false);
      }
    }

    loadCaterer();
  }, [id]);

  if (loading) {
    return <main className="detail-page"><p>Loading caterer and packages...</p></main>;
  }

  if (error || !caterer) {
    return (
      <main className="detail-page">
        <h2>Unable to load caterer</h2>
        <p>{error || "Caterer not found."}</p>
        <Link to="/caterers" className="back-link">Back to Caterers</Link>
      </main>
    );
  }

  const packages = caterer.packages || [];

  return (
    <main className="detail-page">
      <section className="detail-hero">
        <p className="eyebrow">SOKOCATER / CATERER DETAILS</p>
        <span className="detail-category">
          {caterer.category || "Catering Service"}
        </span>
        <h1>{caterer.business_name}</h1>
        <p>{caterer.description || "Discover catering packages for your next event."}</p>
        <p>{caterer.location}</p>
      </section>

      <section className="detail-content">
        <div className="detail-intro">
          <p className="eyebrow">OUR SERVICES</p>
          <h2>Choose Your Catering Package</h2>
          <p>
            Explore the available packages and choose the option
            that suits your event.
          </p>
        </div>

        {packages.length === 0 ? (
          <p>No packages are currently available for this caterer.</p>
        ) : (
          <div className="package-grid">
            {packages.map((item) => (
              <article className="package-card" key={item.id}>
                <h3>{item.package_name}</h3>

                <p className="package-description">
                  {item.description}
                </p>

                <h2 className="package-price">
                  KSh {Number(item.price_per_guest).toLocaleString()}
                  <span> / person</span>
                </h2>

                <p>
                  Minimum guests: {item.minimum_guests}
                </p>

                <p>
                  Maximum guests: {item.maximum_guests ?? "No limit specified"}
                </p>

                {item.menu_items?.length > 0 && (
                  <div className="package-menu">
                    <h4>Included Menu Items</h4>
                    <ul>
                      {item.menu_items.map((menuItem) => (
                        <li key={menuItem.id}>
                          <strong>{menuItem.item_name}</strong>
                          {menuItem.description && (
                            <span> — {menuItem.description}</span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <Link
                  to="/booking"
                  state={{
                    caterer,
                    package: item,
                  }}
                  className="package-button"
                >
                  Choose Package
                </Link>
              </article>
            ))}
          </div>
        )}

        <section className="detail-reviews">
          <h2>Customer Reviews</h2>
          <p>Customer reviews will appear here.</p>
        </section>

        <Link to="/caterers" className="back-link">
          ← Back to Caterers
        </Link>
      </section>
    </main>
  );
}

export default CatererDetail;
