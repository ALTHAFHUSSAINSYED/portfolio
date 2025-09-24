import React from "react";
import "./App.css";
import { Outlet } from "react-router-dom"; // ✨ MODIFIED: ScrollRestoration removed
import { portfolioData } from './data/mock';
import Header from './components/Header';
import Footer from './components/Footer';
import { Toaster } from './components/ui/toaster';
import useManualScroll from './hooks/useManualScroll'; // ✨ NEW: Import our custom hook

function App() {
  // ✨ NEW: Activate our custom scroll restoration hook globally
  useManualScroll();

  return (
    <div className="min-h-screen bg-background flex flex-col overflow-hidden">
      {/* ✨ REMOVED: The conflicting <ScrollRestoration /> component is gone */}
      
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
