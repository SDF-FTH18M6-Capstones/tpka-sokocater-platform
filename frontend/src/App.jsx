
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar";

import Home from "./pages/customer/Home";
import CatererListing from "./pages/customer/CatererListing";
import CatererDetail from "./pages/customer/CatererDetail";
import BookingForm from "./pages/customer/BookingForm";

import Dashboard from "./pages/caterer/Dashboard";
import CatererForm from "./pages/caterer/CatererForm";

import LoginRegister from "./pages/auth/LoginRegister";

import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/caterers" element={<CatererListing />} />
        <Route path="/caterer/:id" element={<CatererDetail />} />
        <Route path="/booking" element={<BookingForm />} />
        <Route path="/login" element={<LoginRegister />} />

        <Route path="/caterer/dashboard" element={<Dashboard />} />
        <Route path="/caterer/profile" element={<CatererForm />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
