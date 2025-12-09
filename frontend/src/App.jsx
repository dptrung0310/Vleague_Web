// src/App.jsx
import React, { useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Home from "./pages/Home/Home";
import Login from "./pages/Auth/Login";
import Register from "./pages/Auth/Register";
import GoogleCallback from "./pages/Auth/GoogleCallBack";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Teams from "./pages/Team/Team";
import Players from "./pages/Players/Players";

function App() {
  return (
    <div className="min-h-screen bg-gray-100 font-sans">
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/teams" element={<Teams />} />
        <Route path="/players" element={<Players />} />
      </Routes>
      <Footer />
    </div>
  );
}

export default App;
