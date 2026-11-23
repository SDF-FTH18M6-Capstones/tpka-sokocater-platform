import { useNavigate } from "react-router-dom";

function CatererDetail() {
  const navigate = useNavigate();

  const caterer = {
    id: 1,
    name: "Elegant Events Catering",
    location: "Nairobi, Kenya",
    phone: "0700 000 000",
    email: "info@example.com",
  };

  return (
    <div className="page-container">
      <h1>{caterer.name}</h1>
      <p>Professional catering services for weddings, parties and corporate events.</p>

      <section>
        <h2>About Our Catering Services</h2>
        <p>We provide quality food and catering services for different occasions.</p>
      </section>

      <section>
        <h2>Our Menu</h2>
        <p>Main Course - KSh 1,000 per person</p>
        <p>Buffet Package - KSh 1,500 per person</p>
        <p>Dessert Package - KSh 500 per person</p>
      </section>

      <button
        type="button"
        onClick={() => navigate("/booking", { state: { caterer } })}
        style={{ cursor: "pointer" }}
      >
        Book This Caterer
      </button>

      <section>
        <h2>Customer Reviews</h2>
        <p>★★★★★</p>
        <p>Excellent catering service!</p>
      </section>

      <section>
        <h2>Contact Information</h2>
        <p>Location: {caterer.location}</p>
        <p>Phone: {caterer.phone}</p>
        <p>Email: {caterer.email}</p>
      </section>
    </div>
  );
}

export default CatererDetail;
