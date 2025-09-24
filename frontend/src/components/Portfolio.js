// src/components/Portfolio.js

import React from 'react';
import { portfolioData } from '../data/mock';
import HeroSection from './HeroSection';
import AboutSection from './AboutSection';
import SkillsSection from './SkillsSection';
import ExperienceSection from './ExperienceSection';
import CertificationsSection from './CertificationsSection';
import ProjectsSection from './ProjectsSection';
import ContactSection from './ContactSection';

// NOTE: Header, Footer, and Toaster are intentionally NOT included here.
// The global layout (Header/Footer/Toaster) is provided by App.js to avoid duplicates.

const Portfolio = () => {
  return (
    // ✨ MODIFIED: Added "relative" to create a stable anchor for the page layout.
    <div className="min-h-screen bg-background relative">
      <HeroSection personalInfo={portfolioData.personalInfo} />
      <AboutSection personalInfo={portfolioData.personalInfo} achievements={portfolioData.achievements}/>
      <SkillsSection skills={portfolioData.skills} />
      <ExperienceSection experience={portfolioData.experience} />
      <CertificationsSection certifications={portfolioData.certifications} />
      <ProjectsSection />
      <ContactSection personalInfo={portfolioData.personalInfo} />
    </div>
  );
};

export default Portfolio;
