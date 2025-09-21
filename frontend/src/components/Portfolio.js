// src/components/Portfolio.js (Updated)

import React from 'react';
// We still use mock data for now for the parts we haven't connected to the API yet.
import { portfolioData } from '../data/mock'; 
import Header from './Header';
import HeroSection from './HeroSection';
import AboutSection from './AboutSection';
import SkillsSection from './SkillsSection';
import ExperienceSection from './ExperienceSection';
import CertificationsSection from './CertificationsSection';
import ProjectsSection from './ProjectsSection';
import ContactSection from './ContactSection';
import Footer from './Footer';
import { Toaster } from './ui/toaster';

const Portfolio = () => {
  return (
    <div className="min-h-screen bg-black neon-theme">
      <Header personalInfo={portfolioData.personalInfo} />
      <HeroSection personalInfo={portfolioData.personalInfo} />
      <AboutSection 
        personalInfo={portfolioData.personalInfo} 
        achievements={portfolioData.achievements}
      />
      <SkillsSection skills={portfolioData.skills} />
      <ExperienceSection experience={portfolioData.experience} />
      <CertificationsSection certifications={portfolioData.certifications} />
      
      {/* ✨ MODIFIED: We are no longer passing the 'projects' prop.
          This component will now fetch its own data from your live database. */}
      <ProjectsSection />
      
      <ContactSection personalInfo={portfolioData.personalInfo} />
      <Footer personalInfo={portfolioData.personalInfo} />
      <Toaster />
    </div>
  );
};

export default Portfolio;
