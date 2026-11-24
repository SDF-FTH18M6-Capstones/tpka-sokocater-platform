import { useState } from "react";
import Button from "../../components/Button";

function CatererProfile() {
  const [caterer] = useState({
    businessName: "Example Caterers",
    category: "Wedding",
    price_range: "Ksh 1000 - 2500 per guest",
    location: "Nairobi, Kikuyu",
    description: "We provide delicious wedding catering with Pilau, Chapati and Nyama Choma.",
    rating: 4.8,
  });

  return (
    <div className="page-container">
      <h1>{caterer.businessName}</h1>
      <p><strong>Category:</strong> {caterer.category}</p>
      <p><strong>Price Range:</strong> {caterer.price_range}</p>
      <p><strong>Location:</strong> {caterer.location}</p>
      <p><strong>Rating:</strong> ⭐ {caterer.rating}</p>
      <p>{caterer.description}</p>
      <Button onClick={() => alert("Booking flow - connect to Allan's page")}>Book This Caterer</Button>
    </div>
  );
}

export default CatererProfile;
