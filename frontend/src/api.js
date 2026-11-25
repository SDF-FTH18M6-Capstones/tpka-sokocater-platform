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
