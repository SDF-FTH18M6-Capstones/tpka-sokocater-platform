import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";

import Home from "./pages/customer/Home";
import CatererListing from "./pages/customer/CatererListing";
import CatererDetail from "./pages/customer/CatererDetail";
import BookingForm from "./pages/customer/BookingForm";

import Dashboard from "./pages/caterer/Dashboard";
import CatererForm from "./pages/caterer/CatererForm";

import Login from "./pages/auth/Login";
import Signup from "./pages/auth/Signup";

import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        {/* Public - anyone can see */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Protected - must login first */}
        <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
        <Route path="/caterers" element={<ProtectedRoute><CatererListing /></ProtectedRoute>} />
        <Route path="/caterer/:id" element={<ProtectedRoute><CatererDetail /></ProtectedRoute>} />
        <Route path="/booking" element={<ProtectedRoute><BookingForm /></ProtectedRoute>} />
        <Route path="/caterer/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/caterer/profile" element={<ProtectedRoute><CatererForm /></ProtectedRoute>} />

        {/* Wrong URL -> go to login */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
