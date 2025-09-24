import React, { useEffect } from 'react';
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
  const location = useLocation();

  useEffect(() => {
    // This effect runs when the page loads or when you navigate back to it
    if (location.state && location.state.scrollPosition) {
      // Use a small timeout to ensure the content has rendered before scrolling
      setTimeout(() => {
        window.scrollTo({ top: location.state.scrollPosition, behavior: 'auto' });
      }, 0);
    }
  }, [location.state]);

  return (
    // ✨ MODIFIED: Replaced 'bg-black neon-theme' with 'bg-background' for theme compatibility
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
