import React from "react";
import "./App.css";
// ✨ MODIFIED: Re-added ScrollRestoration, removed the custom hook import
import { Outlet, ScrollRestoration } from "react-router-dom"; 

import { portfolioData as techAssistantData } from './data/mock';
import Header from './components/Header';
import Footer from './components/Footer';
import { Toaster } from './components/ui/toaster';
import './smooth-scroll';
import Chatbot from './components/Chatbot';

function App() {
  // ✨ REMOVED: The call to the custom hook is gone.
  // useManualScroll();

  return (
    <div className="min-h-screen bg-background flex flex-col overflow-hidden">
      {/* ✨ MODIFIED: The official <ScrollRestoration /> component is back. */}
      <ScrollRestoration />
      
  <Header personalInfo={techAssistantData.personalInfo} />
      
      <main className="flex-grow">
        <Outlet />
      </main>
      
  <Footer personalInfo={techAssistantData.personalInfo} />
      <Toaster />
      <Chatbot />
    </div>
  );
}

export default App;
