
import { Link, useParams } from "react-router-dom";

const caterers = {
  1: {
    name: "Elegant Events Catering",
    category: "Wedding Catering",
    description:
      "Professional catering services for weddings, parties and corporate events.",
  },
  2: {
    name: "Delicious Moments",
    category: "Corporate Events",
    description:
      "Quality meals and catering services for corporate functions and celebrations.",
  },
  3: {
    name: "Perfect Plates",
    category: "Food Catering",
    description:
      "Fresh food and delicious catering for every occasion.",
  },
};

const packages = [
  {
    name: "Main Course",
    price: 1000,
    description: "A delicious main meal for your guests.",
  },
  {
    name: "Buffet Package",
    price: 1500,
    description: "A variety of meals served buffet style.",
    popular: true,
  },
  {
    name: "Dessert Package",
    price: 500,
    description: "Sweet treats and desserts for your event.",
  },
];

function CatererDetail() {
  const { id } = useParams();
  const caterer = caterers[id] || caterers[1];

  return (
    <main className="detail-page">
      <section className="detail-hero">
        <p className="eyebrow">SOKOCATER / CATERER DETAILS</p>
        <span className="detail-category">{caterer.category}</span>
        <h1>{caterer.name}</h1>
        <p>{caterer.description}</p>
      </section>

      <section className="detail-content">
        <div className="detail-intro">
          <p className="eyebrow">OUR SERVICES</p>
          <h2>Choose Your Catering Package</h2>
          <p>
            Explore our available packages and choose the
            option that suits your event.
          </p>
        </div>

        <div className="package-grid">
          {packages.map((item) => (
            <article className="package-card" key={item.name}>
              {item.popular && (
                <span className="popular-label">POPULAR</span>
              )}

              <h3>{item.name}</h3>

              <p className="package-description">
                {item.description}
              </p>

              <h2 className="package-price">
                KSh {item.price.toLocaleString()}
                <span> / person</span>
              </h2>

              <Link to="/booking" className="package-button">
                Choose Package
              </Link>
            </article>
          ))}
        </div>

        <p className="price-note">
          These are demonstration prices for the frontend.
          Actual vendor prices will be confirmed when connected
          to the backend.
        </p>

        <section className="detail-reviews">
          <h2>Customer Reviews</h2>
          <p>★★★★★</p>
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
