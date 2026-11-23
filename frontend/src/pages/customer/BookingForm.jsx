import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

function BookingForm() {
  const location = useLocation();
  const navigate = useNavigate();

  const caterer = location.state?.caterer;
  const selectedPackage = location.state?.package;

  const [formData, setFormData] = useState({
    eventType: "Birthday",
    eventDate: "",
    startTime: "",
    endTime: "",
    guests: "",
    eventLocation: caterer?.location || "",
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setLoading(true);
    setMessage("");
    setError("");

    if (!caterer || !selectedPackage) {
      setError("Please select a caterer and package before booking.");
      setLoading(false);
      return;
    }

    const guests = Number(formData.guests);

    if (guests < selectedPackage.minimum_guests) {
      setError(
        `This package requires at least ${selectedPackage.minimum_guests} guests.`
      );
      setLoading(false);
      return;
    }

    if (
      selectedPackage.maximum_guests != null &&
      guests > selectedPackage.maximum_guests
    ) {
      setError(
        `This package allows a maximum of ${selectedPackage.maximum_guests} guests.`
      );
      setLoading(false);
      return;
    }

    const token =
      localStorage.getItem("sokocater_token") ||
      localStorage.getItem("token") ||
      localStorage.getItem("access_token");

    if (!token) {
      setError("Please log in as a customer before making a booking.");
      setLoading(false);
      return;
    }

    const payload = {
      caterer_id: Number(caterer.id),
      package_id: Number(selectedPackage.id),
      event_type: formData.eventType,
      event_date: formData.eventDate,
      event_start_time: formData.startTime,
      event_end_time: formData.endTime,
      event_location: formData.eventLocation,
      guest_count: guests,
    };

    try {
      const response = await fetch("/api/bookings", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      const result = await response.json();

      if (!response.ok) {
        const details = result.error || result.message || "Booking failed.";

        throw new Error(
          typeof details === "string"
            ? details
            : JSON.stringify(details)
        );
      }

      setMessage(
        `Booking created successfully! Booking ID: ${result.data.id}`
      );

      setTimeout(() => navigate("/customer/dashboard"), 1500);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (!caterer || !selectedPackage) {
    return (
      <main className="page-container">
        <h1>No package selected</h1>
        <p>Please choose a caterer and package before making a booking.</p>
        <Link to="/caterers">Browse Caterers</Link>
      </main>
    );
  }

  return (
    <main className="page-container">
      <h1>Book Your Catering Service</h1>

      <section>
        <h2>{caterer.business_name}</h2>
        <p>Location: {caterer.location}</p>

        <h3>{selectedPackage.package_name}</h3>
        <p>{selectedPackage.description}</p>

        <p>
          Price per guest: KSh{" "}
          {Number(selectedPackage.price_per_guest).toLocaleString()}
        </p>

        <p>Minimum guests: {selectedPackage.minimum_guests}</p>

        {selectedPackage.maximum_guests != null && (
          <p>Maximum guests: {selectedPackage.maximum_guests}</p>
        )}
      </section>

      {message && <p role="status">{message}</p>}
      {error && <p role="alert">{error}</p>}

      <form onSubmit={handleSubmit}>
        <label htmlFor="eventType">Event Type</label>
        <select
          id="eventType"
          name="eventType"
          value={formData.eventType}
          onChange={handleChange}
          required
        >
          <option value="Wedding">Wedding</option>
          <option value="Birthday">Birthday</option>
          <option value="Corporate">Corporate Event</option>
          <option value="Private">Private Event</option>
        </select>

        <label htmlFor="eventDate">Event Date</label>
        <input
          id="eventDate"
          name="eventDate"
          type="date"
          value={formData.eventDate}
          onChange={handleChange}
          required
        />

        <label htmlFor="startTime">Event Start Time</label>
        <input
          id="startTime"
          name="startTime"
          type="time"
          value={formData.startTime}
          onChange={handleChange}
          required
        />

        <label htmlFor="endTime">Event End Time</label>
        <input
          id="endTime"
          name="endTime"
          type="time"
          value={formData.endTime}
          onChange={handleChange}
          required
        />

        <label htmlFor="guests">Number of Guests</label>
        <input
          id="guests"
          name="guests"
          type="number"
          min={selectedPackage.minimum_guests}
          max={selectedPackage.maximum_guests || undefined}
          value={formData.guests}
          onChange={handleChange}
          required
        />

        <label htmlFor="eventLocation">Event Location</label>
        <input
          id="eventLocation"
          name="eventLocation"
          type="text"
          value={formData.eventLocation}
          onChange={handleChange}
          required
        />

        <button type="submit" disabled={loading}>
          {loading ? "Submitting..." : "Submit Booking"}
        </button>
      </form>
    </main>
  );
}

export default BookingForm;