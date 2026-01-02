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

      // ✨ IMPORTANT: Skip scroll for 'blogs' and 'projects' sections
      // These sections have their own data loading logic and will handle scroll after data loads
      // to prevent double-jump glitch and long smooth scroll hijacking
      if (targetId === 'blogs' || targetId === 'projects') {
        return;
      }

      // Function to perform safe scroll
      const performScroll = (behavior = 'auto') => {
        const element = document.getElementById(targetId);
        if (element) {
          element.scrollIntoView({ block: 'start', behavior });
        }
      };

      // 1. Initial Instant Scroll
      document.documentElement.style.scrollBehavior = 'auto';
      performScroll('auto');

      // Re-enable smooth scrolling
      setTimeout(() => {
        document.documentElement.style.scrollBehavior = 'smooth';
      }, 50);

      // 2. Retry scrolls to handle dynamic content loading (layout shifts)
      // Checks again after short delays to ensure we stay on target if sections above expand
      setTimeout(() => performScroll('auto'), 150);
      setTimeout(() => performScroll('smooth'), 600);

      // Clear state
      window.history.replaceState({}, document.title);
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
