const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api";

async function getJson(path) {
  const res = await fetch(`${API_URL}${path}`);
  return await res.json();
}

export async function getCaterers() {
  return getJson("/caterers");
}

export async function getBookings() {
  return getJson("/bookings");
}

export async function createBooking(payload) {
  const res = await fetch(`${API_URL}/bookings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return await res.json();
}

export async function createCaterer(payload) {
  const res = await fetch(`${API_URL}/caterers`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return await res.json();
}