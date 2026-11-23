
import { useSearchParams, Link } from "react-router-dom";

const caterers = [
  {
    id: 1,
    name: "Elegant Events Catering",
    description: "Professional catering for weddings and private events.",
    category: "Wedding Catering",
    image:
      "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&w=800&q=85",
  },
  {
    id: 2,
    name: "Delicious Moments",
    description: "Quality meals for birthdays and corporate events.",
    category: "Corporate Events",
    image:
      "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=85",
  },
  {
    id: 3,
    name: "Perfect Plates",
    description: "Fresh food and catering for every occasion.",
    category: "Food Catering",
    image:
      "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=800&q=85",
  },
];

function CatererListing() {
  const [searchParams] = useSearchParams();
  const selectedCategory = searchParams.get("category");

  const filteredCaterers = caterers.filter((caterer) => {
    return !selectedCategory || caterer.category === selectedCategory;
  });

  return (
    <main className="listing-page">
      <section className="listing-hero">
        <p className="eyebrow">DISCOVER SOKOCATER</p>
        <h1>{selectedCategory || "Find the Perfect Caterer"}</h1>
        <p>
          Discover trusted catering professionals and make
          your next event unforgettable.
        </p>
      </section>

      <section className="listing-content">
        <div className="listing-heading">
          <div>
            <p className="eyebrow">OUR CATERERS</p>
            <h2>Explore Available Services</h2>
          </div>

          <Link to="/caterers" className="clear-filter">
            View All Caterers
          </Link>
        </div>

        {filteredCaterers.length > 0 ? (
          <div className="caterer-list">
            {filteredCaterers.map((caterer) => (
              <article className="caterer-card" key={caterer.id}>
                <img
                  src={caterer.image}
                  alt={caterer.name}
                  className="caterer-image"
                />

                <div className="caterer-card-content">
                  <span className="caterer-category">
                    {caterer.category}
                  </span>

                  <h3>{caterer.name}</h3>
                  <p>{caterer.description}</p>

                  <Link
                    to={`/caterer/${caterer.id}`}
                    className="caterer-button"
                  >
                    View Details →
                  </Link>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="empty-listing">
            <h3>No caterers found yet</h3>
            <p>We're working on adding more catering professionals.</p>
            <Link to="/caterers">Browse all caterers</Link>
          </div>
        )}
      </section>
    </main>
  );
}

export default CatererListing;
