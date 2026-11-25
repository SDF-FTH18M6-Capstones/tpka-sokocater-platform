import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";

import Home from "./pages/customer/Home";
import BrowseCaterers from "./pages/customer/BrowseCaterers";
import CatererDetail from "./pages/customer/CatererDetail";
import BookingForm from "./pages/customer/BookingForm";
import MyBookings from "./pages/customer/MyBookings";

import Dashboard from "./pages/caterer/Dashboard";
import CatererForm from "./pages/caterer/CatererForm";
import CreatePackage from "./pages/caterer/CreatePackage";
import CatererProfile from "./pages/caterer/CatererProfile";

import Login from "./pages/auth/Login";
import Signup from "./pages/auth/Signup";

import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Customer routes */}
        <Route path="/" element={<Home />} />

        <Route
          path="/caterers"
          element={
            <ProtectedRoute>
              <BrowseCaterers />
            </ProtectedRoute>
          }
        />

        <Route
          path="/caterer/:id"
          element={
            <ProtectedRoute>
              <CatererDetail />
            </ProtectedRoute>
          }
        />

        <Route
          path="/booking"
          element={
            <ProtectedRoute>
              <BookingForm />
            </ProtectedRoute>
          }
        />

        <Route
          path="/my-bookings"
          element={
            <ProtectedRoute allowedRoles={["customer"]}>
              <MyBookings />
            </ProtectedRoute>
          }
        />

        {/* Caterer routes - CATERER ONLY */}
        <Route
          path="/caterer/dashboard"
          element={
            <ProtectedRoute allowedRoles={["caterer", "admin"]}>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/caterer/profile"
          element={
            <ProtectedRoute allowedRoles={["caterer", "admin"]}>
              <CatererForm />
            </ProtectedRoute>
          }
        />

        <Route
          path="/caterer/create-package"
          element={
            <ProtectedRoute allowedRoles={["caterer", "admin"]}>
              <CreatePackage />
            </ProtectedRoute>
          }
        />

        <Route path="/caterer/view-profile/:id" element={<CatererProfile />} />
        <Route path="/caterer/view-profile" element={<CatererProfile />} />

        {/* Unknown routes */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
