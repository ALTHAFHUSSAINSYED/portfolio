// src/App.js

import React from "react";
import "./App.css";
// ✨ MODIFIED: Outlet renders the current page's content, ScrollRestoration handles scrolling
import { Outlet, ScrollRestoration } from "react-router-dom";
import { portfolioData } from './data/mock';
import Header from './components/Header';
import Footer from './components/Footer';
import { Toaster } from './components/ui/toaster';

function App() {
  return (
    // This div now serves as the main layout container
    <div className="min-h-screen bg-background">
      {/* This component will now correctly manage scroll positions */}
      <ScrollRestoration />

      <Header personalInfo={portfolioData.personalInfo} />
      <main>
        {/* The content for your routes (Portfolio or ProjectDetailPage) will be rendered here */}
        <Outlet />
      </main>
      <Footer personalInfo={portfolioData.personalInfo} />
      <Toaster />
    </div>
  );
}

export default App;
