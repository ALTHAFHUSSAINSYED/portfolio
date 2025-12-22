// src/components/TechAssistant.js

import React from 'react';
import portfolioData from '../data/portfolio_data.json';
import HeroSection from './HeroSection';
import AboutSection from './AboutSection';
import SkillsSection from './SkillsSection';
import ExperienceSection from './ExperienceSection';
import CertificationsSection from './CertificationsSection';
import ProjectsSection from './ProjectsSection';
import BlogsSection from './BlogsSection';
import ContactSection from './ContactSection';

// NOTE: Header, Footer, and Toaster are intentionally NOT included here.
// The global layout (Header/Footer/Toaster) is provided by App.js to avoid duplicates.

const TechAssistant = () => {
  return (
    // ✨ MODIFIED: Added "relative" to create a stable anchor for the page layout.
    <div className="min-h-screen bg-background relative">
      <HeroSection personalInfo={portfolioData.personal_info} />
      <AboutSection personalInfo={portfolioData.personal_info} achievements={portfolioData.achievements} />
      <SkillsSection skills={portfolioData.skills} />
      <ExperienceSection experience={portfolioData.experience} />
      <CertificationsSection certifications={portfolioData.certifications} />
      <ProjectsSection />
      <BlogsSection />
      <ContactSection personalInfo={portfolioData.personal_info} />
    </div>
  );
};

export default TechAssistant;
