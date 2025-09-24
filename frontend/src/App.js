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
    // ✨ --- ROBUST FIX: Added "relative isolate" classes --- ✨
    // "relative" creates the containing block for the orbs.
    // "isolate" creates a new stacking context, a best practice for complex layouts.
    <div className="min-h-screen bg-background relative isolate">
      
      <ScrollRestoration />

      <Header personalInfo={portfolioData.personalInfo} />
      <main>
        <Outlet />
      </main>
      <Footer personalInfo={portfolioData.personalInfo} />
      <Toaster />
    </div>
  );
}

export default App;
