// src/App.js

import React from "react";
import "./App.css";
import { Outlet, ScrollRestoration } from "react-router-dom";
import { portfolioData } from './data/mock';
import Header from './components/Header';
import Footer from './components/Footer';
import { Toaster } from './components/ui/toaster';

function App() {
  return (
    // ✨ MODIFIED: Changed to a flex column layout for a sticky footer.
    <div className="min-h-screen bg-background flex flex-col">
      <ScrollRestoration />

      <Header personalInfo={portfolioData.personalInfo} />
      
      {/* ✨ MODIFIED: The main content area now grows to fill available space. */}
      <main className="flex-grow">
        <Outlet />
      </main>
      
      <Footer personalInfo={portfolioData.personalInfo} />
      <Toaster />
    </div>
  );
}

export default App;
