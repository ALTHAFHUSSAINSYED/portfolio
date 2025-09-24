// src/App.js

import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Portfolio from "./components/Portfolio";
import ProjectDetailPage from "./components/ProjectDetailPage"; // ✨ NEW: Import the new component

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          {/* This is the route for your main portfolio homepage */}
          <Route path="/" element={<Portfolio />} />

          {/* ✨ NEW: This is the new route for the project details page */}
          <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
