import React from 'react';
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

const Portfolio = () => {
  return (
    <div className="min-h-screen bg-white">
      <Header personalInfo={portfolioData.personalInfo} />
      <HeroSection personalInfo={portfolioData.personalInfo} />
      <AboutSection 
        personalInfo={portfolioData.personalInfo} 
        achievements={portfolioData.achievements}
      />
      <SkillsSection skills={portfolioData.skills} />
      <ExperienceSection experience={portfolioData.experience} />
      <CertificationsSection certifications={portfolioData.certifications} />
      <ProjectsSection projects={portfolioData.projects} />
      <ContactSection personalInfo={portfolioData.personalInfo} />
      <Footer personalInfo={portfolioData.personalInfo} />
    </div>
  );
};

export default Portfolio;