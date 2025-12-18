import React from "react";
import "./App.css";
import { Outlet, ScrollRestoration } from "react-router-dom"; 
import { HelmetProvider } from 'react-helmet-async';

import { portfolioData as techAssistantData } from './data/mock';
import Header from './components/Header';
import Footer from './components/Footer';
import { Toaster } from './components/ui/toaster';
import './smooth-scroll';
import Chatbot from './components/Chatbot';

function App() {
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
