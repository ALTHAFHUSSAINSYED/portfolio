import React, { useLayoutEffect } from "react";
import "./App.css";
import { Outlet, ScrollRestoration, useLocation } from "react-router-dom"; 
import { HelmetProvider } from 'react-helmet-async';

import { portfolioData as techAssistantData } from './data/mock';
import Header from './components/Header';
import Footer from './components/Footer';
import { Toaster } from './components/ui/toaster';
import './smooth-scroll';
import Chatbot from './components/Chatbot';

function App() {
  const location = useLocation();

  // useLayoutEffect runs BEFORE the screen paints (Invisible to user)
  useLayoutEffect(() => {
    if (location.state && location.state.scrollTo) {
      const targetId = location.state.scrollTo;
      const element = document.getElementById(targetId);
      
      if (element) {
        // 1. Temporarily disable smooth scrolling to force an instant JUMP
        document.documentElement.style.scrollBehavior = 'auto';
        
        // 2. Teleport to the section
        element.scrollIntoView({ block: 'start' });
        
        // 3. Re-enable smooth scrolling after a tiny delay
        setTimeout(() => {
          document.documentElement.style.scrollBehavior = 'smooth';
        }, 50);
        
        // 4. Clear the state so it doesn't happen on refresh
        window.history.replaceState({}, document.title);
      }
    }
  }, [location]);

  return (
    <HelmetProvider>
      <div className="min-h-screen bg-background flex flex-col overflow-hidden">
        <ScrollRestoration />
        
        <Header personalInfo={techAssistantData.personalInfo} />
        
        <main className="flex-grow">
          <Outlet />
        </main>
        
        <Footer personalInfo={techAssistantData.personalInfo} />
        <Toaster />
        <Chatbot />
      </div>
    </HelmetProvider>
  );
}

export default App;
