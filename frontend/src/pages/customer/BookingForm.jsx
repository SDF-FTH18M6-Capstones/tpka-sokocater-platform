import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import Input from "../../components/Input";
import Select from "../../components/Select";
import Button from "../../components/Button";
import { createBooking } from "../../api";

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
    guests: String(selectedPackage?.minimum_guests || 40),
    eventLocation: "",
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  function handleChange(e) {
    const { name, value } = e.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage("");
    setError("");

    if (!caterer || !selectedPackage) {
      setError("Please select a caterer and package before booking.");
      return;
    }

    const token = localStorage.getItem("sokocater_token");

    if (!token) {
      setError("Please log in before making a booking.");
      return;
    }

    const guestCount = Number(formData.guests);

    if (
      guestCount < selectedPackage.minimum_guests ||
      (
        selectedPackage.maximum_guests &&
        guestCount > selectedPackage.maximum_guests
      )
    ) {
      setError(
        `This package accepts ${selectedPackage.minimum_guests} to ${selectedPackage.maximum_guests} guests.`
      );
      return;
    }

    if (formData.startTime >= formData.endTime) {
      setError("Event end time must be later than event start time.");
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
      guest_count: guestCount,
    };

    try {
      setLoading(true);

      const data = await createBooking(payload);

      setMessage(
        `Booking created successfully! Booking ID: ${data.data.id}. Estimated total: KSh ${Number(data.data.estimated_total).toLocaleString()}`
      );

      setTimeout(() => navigate("/"), 2000);
    } catch (err) {
      setError(err.message || "Unable to create booking.");
    } finally {
      setLoading(false);
    }
  }

  if (!caterer || !selectedPackage) {
    return (
      <main className="page-container">
        <h1>No Package Selected</h1>
        <p>Please choose a caterer and package before continuing.</p>
        <Link to="/caterers">Browse Caterers</Link>
      </main>
    );
  }

  return (
    <main className="page-container">
      <h1>Book Your Catering Service</h1>

      <div
        style={{
          background: "#f0f7ff",
          padding: "16px",
          borderRadius: "8px",
          marginBottom: "20px",
        }}
      >
        <h3>Booking Summary</h3>
        <p><strong>Caterer:</strong> {caterer.business_name}</p>
        <p><strong>Location:</strong> {caterer.location}</p>
        <p><strong>Package:</strong> {selectedPackage.package_name}</p>
        <p>
          <strong>Price per guest:</strong> KSh{" "}
          {Number(selectedPackage.price_per_guest).toLocaleString()}
        </p>
        <p>
          <strong>Guest range:</strong>{" "}
          {selectedPackage.minimum_guests} –{" "}
          {selectedPackage.maximum_guests ?? "No maximum specified"}
        </p>
      </div>

      {message && (
        <p style={{ color: "green", fontWeight: "bold" }}>{message}</p>
      )}

      {error && (
        <p style={{ color: "red", fontWeight: "bold" }}>{error}</p>
      )}

      <form onSubmit={handleSubmit}>
        <Select
          label="Event Type"
          name="eventType"
          value={formData.eventType}
          onChange={handleChange}
          options={[
            { value: "Wedding", label: "Wedding" },
            { value: "Birthday", label: "Birthday" },
            { value: "Corporate", label: "Corporate Event" },
            { value: "Private", label: "Private Event" },
          ]}
        />

        <Input
          label="Event Date"
          name="eventDate"
          type="date"
          value={formData.eventDate}
          onChange={handleChange}
        />

        <Input
          label="Event Start Time"
          name="startTime"
          type="time"
          value={formData.startTime}
          onChange={handleChange}
        />

        <Input
          label="Event End Time"
          name="endTime"
          type="time"
          value={formData.endTime}
          onChange={handleChange}
        />

        <Input
          label="Number of Guests"
          name="guests"
          type="number"
          value={formData.guests}
          onChange={handleChange}
          placeholder="Enter number of guests"
        />

        <Input
          label="Event Location"
          name="eventLocation"
          value={formData.eventLocation}
          onChange={handleChange}
          placeholder="Enter event venue"
        />

        <Button type="submit" disabled={loading}>
          {loading ? "Submitting..." : "Submit Booking"}
        </Button>
      </form>
    </main>
  );
}

export default BookingForm;
