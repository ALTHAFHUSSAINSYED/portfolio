// src/App.js

import React from "react";
import "./App.css";
// ✨ MODIFIED: Import ScrollRestoration
import { BrowserRouter, Routes, Route, ScrollRestoration } from "react-router-dom";
import Portfolio from "./components/Portfolio";
import ProjectDetailPage from "./components/ProjectDetailPage";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        {/* ✨ NEW: Add the official ScrollRestoration component here */}
        <ScrollRestoration />
        <Routes>
          {/* This is the route for your main portfolio homepage */}
          <Route path="/" element={<Portfolio />} />

          {/* This is the new route for the project details page */}
          <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
