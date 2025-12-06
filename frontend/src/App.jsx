// src/App.jsx
import React, { useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Home from "./pages/Home/Home";
import Login from "./pages/Auth/Login";
import Register from "./pages/Auth/Register";
import GoogleCallback from "./pages/Auth/GoogleCallBack";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Teams from "./pages/Team/Team";
import Players from "./pages/Players/Players";

// Layout component
const DefaultLayout = ({ children }) => (
  <div className="min-h-screen flex flex-col">
    <Navbar />
    <main className="flex-grow">{children}</main>
    <Footer />
  </div>
);

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route
            path="/login"
            element={
              <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100">
                <Login />
              </div>
            }
          />

          <Route
            path="/register"
            element={
              <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100">
                <Register />
              </div>
            }
          />

          <Route path="/auth/google/callback" element={<GoogleCallback />} />

          {/* Home Page */}
          <Route
            path="/"
            element={
              <DefaultLayout>
                <Home />
              </DefaultLayout>
            }
          />

          <Route
            path="/teams"
            element={
              <DefaultLayout>
                <Teams />
              </DefaultLayout>
            }
          />

          <Route
            path="/players"
            element={
              <DefaultLayout>
                <Players />
              </DefaultLayout>
            }
          />

          {/* Redirect any unknown routes to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
