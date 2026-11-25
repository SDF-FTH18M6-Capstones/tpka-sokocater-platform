const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api";

function authHeaders() {
  const token = localStorage.getItem("sokocater_token");

  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function handleRes(res) {
  const data = await res.json().catch(() => ({}));

  if (res.status === 401) {
    localStorage.removeItem("sokocater_token");
    localStorage.removeItem("sokocater_user");

    if (!window.location.pathname.includes("/login")) {
      window.location.href = "/login";
    }
  }

  if (!res.ok) {
    const msg = data.message || data.error || "Request failed";
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }

  return data;
}

export async function getCaterers(params = {}) {
  const query = new URLSearchParams();
  if (params.min_price) query.append("min_price", params.min_price);
  if (params.max_price) query.append("max_price", params.max_price);
  if (params.category) query.append("category", params.category);
  const qs = query.toString() ? "?" + query.toString() : "";
  const res = await fetch(API_URL + "/caterers" + qs, {
    headers: authHeaders(),
  });

  return handleRes(res);
}

export async function getCatererById(id) {
  const res = await fetch(`${API_URL}/caterers/${id}`, {
    headers: authHeaders(),
  });

  return handleRes(res);
}

export async function getBookings() {
  const res = await fetch(`${API_URL}/bookings`, {
    headers: authHeaders(),
  });

  return handleRes(res);
}

export async function createBooking(payload) {
  const res = await fetch(`${API_URL}/bookings`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });

  return handleRes(res);
}

export async function createCaterer(payload) {
  const res = await fetch(`${API_URL}/caterers`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });

  return handleRes(res);
}

export async function updateCaterer(id, payload) {
  const res = await fetch(`${API_URL}/caterers/${id}`, {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });

  return handleRes(res);
}

export async function deleteCaterer(id) {
  const res = await fetch(`${API_URL}/caterers/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });

  return handleRes(res);
}

export async function getPackages() {
  const res = await fetch(`${API_URL}/packages`, {
    headers: authHeaders(),
  });

  return handleRes(res);
}

export async function updateBooking(id, status) {
  const res = await fetch(`${API_URL}/bookings/${id}`, {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify({ status }),
  });
  return handleRes(res);
}

export async function deleteBooking(id) {
  const res = await fetch(`${API_URL}/bookings/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  return handleRes(res);
}

export async function createPackage(payload) {
  const res = await fetch(`${API_URL}/packages`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  return handleRes(res);
}

export async function updatePackage(id, payload) {
  const res = await fetch(`${API_URL}/packages/${id}`, {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  return handleRes(res);
}

export async function deletePackage(id) {
  const res = await fetch(`${API_URL}/packages/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  return handleRes(res);
}

export async function getMenus() {
  const res = await fetch(`${API_URL}/menus`, { headers: authHeaders() });
  return handleRes(res);
}
export async function createMenu(payload) {
  const res = await fetch(`${API_URL}/menus`, { method: "POST", headers: authHeaders(), body: JSON.stringify(payload) });
  return handleRes(res);
}
export async function getMenuItems() {
  const res = await fetch(`${API_URL}/menu-items`, { headers: authHeaders() });
  return handleRes(res);
}
export async function createMenuItem(payload) {
  const res = await fetch(`${API_URL}/menu-items`, { method: "POST", headers: authHeaders(), body: JSON.stringify(payload) });
  return handleRes(res);
}
export async function deleteMenu(id) {
  const res = await fetch(`${API_URL}/menus/${id}`, { method: "DELETE", headers: authHeaders() });
  return handleRes(res);
}
export async function deleteMenuItem(id) {
  const res = await fetch(`${API_URL}/menu-items/${id}`, { method: "DELETE", headers: authHeaders() });
  return handleRes(res);
}

// ============================================================
// PAYMENTS - matches backend/routes/payment_routes.py
// ============================================================

export async function createPayment(booking_id, payment_method) {
  const res = await fetch(`${API_URL}/payments`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ booking_id, payment_method }),
  });
  return handleRes(res);
}

export async function getPayments() {
  const res = await fetch(`${API_URL}/payments`, {
    headers: authHeaders(),
  });
  return handleRes(res);
}

export async function getPayment(id) {
  const res = await fetch(`${API_URL}/payments/${id}`, {
    headers: authHeaders(),
  });
  return handleRes(res);
}

export async function simulatePayment(id, result) {
  const res = await fetch(`${API_URL}/payments/${id}/simulate`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ result }),
  });
  return handleRes(res);
}

// ============================================================
// REVIEWS - matches backend/routes/review_routes.py
// ============================================================

export async function createReview(booking_id, rating, comment) {
  // Exactly { booking_id, rating, comment } - no extra keys
  // booking_id: int > 0, rating: int 1-5, comment: string or null
  // Only works if booking.status === "completed", else 400
  // 409 if booking already reviewed
  const res = await fetch(`${API_URL}/reviews`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ booking_id, rating, comment: comment || null }),
  });
  return handleRes(res);
}

export async function getCatererReviews(caterer_id) {
  const res = await fetch(`${API_URL}/caterers/${caterer_id}/reviews`, {
    headers: authHeaders(),
  });
  return handleRes(res);
}

// ============================================================
// NOTIFICATIONS - matches backend/routes/notification_routes.py
// ============================================================

export async function getNotifications() {
  const res = await fetch(`${API_URL}/notifications`, {
    headers: authHeaders(),
  });
  return handleRes(res);
}

export async function getNotification(id) {
  const res = await fetch(`${API_URL}/notifications/${id}`, {
    headers: authHeaders(),
  });
  return handleRes(res);
}

export async function markNotificationRead(id) {
  // PATCH, no body
  const res = await fetch(`${API_URL}/notifications/${id}/read`, {
    method: "PATCH",
    headers: authHeaders(),
  });
  return handleRes(res);
}

export async function markAllNotificationsRead() {
  // PATCH, no body - must be called before /:id/read route conflicts
  // Note: backend has /read-all AFTER /<id>/read, so "read-all" would 404 as id
  // If this 404s, call markNotificationRead() in a loop instead
  const res = await fetch(`${API_URL}/notifications/read-all`, {
    method: "PATCH",
    headers: authHeaders(),
  });
  return handleRes(res);
}
