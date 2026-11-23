import { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";

function CatererDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [caterer, setCaterer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function fetchCaterer() {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(`/api/caterers/${id}`);
        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.error || "Unable to load caterer details.");
        }

        if (!cancelled) {
          setCaterer(result.data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchCaterer();

    return () => {
      cancelled = true;
    };
  }, [id]);

  if (loading) {
    return <main className="detail-page"><p>Loading caterer details...</p></main>;
  }

  if (error) {
    return (
      <main className="detail-page">
        <h2>Unable to load caterer</h2>
        <p>{error}</p>
        <Link to="/caterers" className="back-link">Back to Caterers</Link>
      </main>
    );
  }

  if (!caterer) {
    return <main className="detail-page"><p>Caterer not found.</p></main>;
  }

  return (
    <main className="detail-page">
      <section className="detail-hero">
        <p className="eyebrow">SOKOCATER / CATERER DETAILS</p>

        {caterer.business_image && (
          <img
            src={caterer.business_image}
            alt={caterer.business_name}
            className="caterer-image"
          />
        )}

        <h1>{caterer.business_name}</h1>
        <p>{caterer.description || "Explore this caterer's available services and packages."}</p>
        <p>{caterer.location}</p>
      </section>

      <section className="detail-content">
        <div className="detail-intro">
          <p className="eyebrow">OUR SERVICES</p>
          <h2>Choose Your Catering Package</h2>
          <p>Compare available packages and select one for your event.</p>
        </div>

        {caterer.packages?.length > 0 ? (
          <div className="package-grid">
            {caterer.packages.map((item) => (
              <article className="package-card" key={item.id}>
                <h3>{item.package_name}</h3>

                <p className="package-description">
                  {item.description || "Catering package"}
                </p>

                <h2 className="package-price">
                  KSh {Number(item.price_per_guest).toLocaleString()}
                  <span> / person</span>
                </h2>

                <p>
                  Minimum guests: {item.minimum_guests}
                </p>

                {item.maximum_guests != null && (
                  <p>Maximum guests: {item.maximum_guests}</p>
                )}

                {item.menu_items?.length > 0 && (
                  <div>
                    <h4>Included Menu Items</h4>
                    <ul>
                      {item.menu_items.map((menuItem) => (
                        <li key={menuItem.id}>
                          <strong>{menuItem.item_name}</strong>
                          {menuItem.description && ` — ${menuItem.description}`}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <button
                  type="button"
                  className="package-button"
                  onClick={() =>
                    navigate("/booking", {
                      state: {
                        caterer,
                        package: item,
                      },
                    })
                  }
                >
                  Choose This Package
                </button>
              </article>
            ))}
          </div>
        ) : (
          <p>No packages are currently available from this caterer.</p>
        )}

        <section className="detail-reviews">
          <h2>Contact Information</h2>
          <p>Location: {caterer.location}</p>
          {caterer.contact_number && (
            <p>Phone: {caterer.contact_number}</p>
          )}
        </section>

        <Link to="/caterers" className="back-link">
          Back to Caterers
        </Link>
      </section>
    </main>
  );
}

export default CatererDetail;
