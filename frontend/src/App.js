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
    // ✨ MODIFIED: Added "overflow-hidden" to contain all content and prevent scrollbars.
    <div className="min-h-screen bg-background flex flex-col overflow-hidden">
      <ScrollRestoration />

      <Header personalInfo={portfolioData.personalInfo} />
      
      <main className="flex-grow">
        <Outlet />
      </main>
      
      <Footer personalInfo={portfolioData.personalInfo} />
      <Toaster />
    </div>
  );
}

export default App;
