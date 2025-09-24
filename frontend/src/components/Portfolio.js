import React from 'react'; // Removed useEffect as it's no longer needed here
import { useLocation } from 'react-router-dom';
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
  // The useEffect for scroll restoration has been removed from this file.
  // The new, more reliable logic will be added to ProjectsSection.js in the next step.

  return (
    <div className="min-h-screen bg-background">
      <Header personalInfo={portfolioData.personalInfo} />
      <HeroSection personalInfo={portfolioData.personalInfo} />
      <AboutSection personalInfo={portfolioData.personalInfo} achievements={portfolioData.achievements}/>
      <SkillsSection skills={portfolioData.skills} />
      <ExperienceSection experience={portfolioData.experience} />
      <CertificationsSection certifications={portfolioData.certifications} />
      <ProjectsSection />
      <ContactSection personalInfo={portfolioData.personalInfo} />
      <Footer personalInfo={portfolioData.personalInfo} />
      <Toaster />
    </div>
  );
};

export default Portfolio;
