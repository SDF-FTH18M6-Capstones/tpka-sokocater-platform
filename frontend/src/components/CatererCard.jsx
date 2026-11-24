import { Link } from "react-router-dom";
import heroImage from "../assets/hero.png";

function CatererCard({ caterer }) {
  const priceRange = caterer.price_range;
  const hasPrices = priceRange?.min_price && priceRange?.max_price;

  return (
    <article className="caterer-card">
      <img
        className="caterer-image"
        src={caterer.business_image || heroImage}
        alt={caterer.business_name}
        onError={(event) => {
          event.currentTarget.onerror = null;
          event.currentTarget.src = heroImage;
        }}
      />

      <div className="caterer-card-content">
        <span className="caterer-category">Catering Service</span>
        <h3>{caterer.business_name}</h3>
        <p>{caterer.location}</p>

        {caterer.description && <p>{caterer.description}</p>}

        <p>
          <strong>Package prices: </strong>
          {hasPrices
            ? `Ksh ${priceRange.min_price} - ${priceRange.max_price} per guest`
            : "Contact caterer for prices"}
        </p>

        <Link to={`/caterer/${caterer.id}`} className="caterer-button">
          View Packages
        </Link>
      </div>
    </article>
  );
}

export default CatererCard;