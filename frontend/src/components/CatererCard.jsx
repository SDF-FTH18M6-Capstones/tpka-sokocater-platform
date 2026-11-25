import { Link } from "react-router-dom";

const CATEGORY_IMAGES = {
  "Weddings": "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&w=800&q=80",
  "Corporate Events": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=80",
  "Food Catering": "https://images.unsplash.com/photo-1555244162-803834f70033?auto=format&fit=crop&w=800&q=80",
};

const DEFAULT_IMAGE = "https://images.unsplash.com/photo-1555244162-803834f70033?auto=format&fit=crop&w=800&q=80";

function CatererCard({ caterer }) {
  const priceRange = caterer.price_range;
  const hasPrices = priceRange?.min_price && priceRange?.max_price;
  const fallbackImage = CATEGORY_IMAGES[caterer.category] || DEFAULT_IMAGE;
  const imageSrc = caterer.business_image && caterer.business_image.startsWith("http") ? caterer.business_image : fallbackImage;

  return (
    <article className="caterer-card">
      <img
        className="caterer-image"
        src={imageSrc}
        alt={caterer.business_name}
        onError={(event) => {
          event.currentTarget.onerror = null;
          event.currentTarget.src = fallbackImage;
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