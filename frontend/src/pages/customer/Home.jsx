
import { Link } from "react-router-dom";

const categories = [
  {
    name: "Food Catering",
    description: "Delicious meals for every occasion.",
    image:
      "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=800&q=85",
  },
  {
    name: "Wedding Catering",
    description: "Make your special day memorable.",
    image:
      "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&w=800&q=85",
  },
  {
    name: "Corporate Events",
    description: "Professional catering for businesses.",
    image:
      "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=85",
  },
];

function Home() {
  return (
    <main>
      {/* HERO SECTION */}
      <section className="hero">
        <div className="hero-content">
          <p className="eyebrow">WELCOME TO SOKOCATER</p>

          <h1>
            Great Food.
            <br />
            Perfect Events.
          </h1>

          <p>
            Discover trusted catering professionals for weddings,
            corporate events, parties, and more.
          </p>

          <div className="hero-actions">
            <a href="#categories" className="primary-button">
              Explore Catering
            </a>

            <Link
              to="/caterer/profile"
              className="secondary-button"
            >
              Become a Caterer
            </Link>

            <Link
              to="/caterer/dashboard"
              className="dashboard-button"
            >
              Open Dashboard
            </Link>
          </div>
        </div>
      </section>

      {/* CATERING CATEGORIES */}
      <section className="categories" id="categories">
        <div className="section-heading">
          <p className="eyebrow">EXPLORE OUR SERVICES</p>
          <h2>Find Catering for Every Occasion</h2>
          <p>Choose the service that suits your event.</p>
        </div>

        <div className="category-grid">
          {categories.map((category) => (
            <article className="category-card" key={category.name}>
              <img
                src={category.image}
                alt={category.name}
                className="category-image"
                loading="lazy"
              />

              <div className="category-card-content">
                <h3>{category.name}</h3>
                <p>{category.description}</p>

                <Link
                  to={`/caterers?category=${encodeURIComponent(category.name)}`}
                >
                  Explore services →
                </Link>
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* ABOUT SECTION */}
      <section className="about" id="about">
        <div>
          <p className="eyebrow">ABOUT SOKOCATER</p>

          <h2>Connecting people with great catering.</h2>

          <p>
            SokoCater brings customers and catering businesses
            together through one convenient marketplace.
            Discover great food, connect with professionals,
            and make every event memorable.
          </p>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="footer">
        <p>© 2026 SokoCater. All rights reserved.</p>
      </footer>
    </main>
  );
}

export default Home;
