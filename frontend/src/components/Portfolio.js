// src/components/TechAssistant.js

import React from 'react';
import portfolioData from '../data/portfolio_data.json';
import SEO from './SEO';
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
  // Homepage SEO
  const homeStructuredData = {
    "@context": "https://schema.org",
    "@type": "Person",
    "@id": "https://althafportfolio.site/#person",
    "name": "Althaf Hussain Syed",
    "jobTitle": "DevOps Engineer | Cloud & Infrastructure Engineer",
    "description": "Certified DevOps Engineer with expertise in AWS, Azure, Kubernetes, and Cloud Infrastructure Engineering. Specializing in CI/CD automation, infrastructure as code, and scalable cloud solutions.",
    "url": "https://althafportfolio.site",
    "image": "https://althafportfolio.site/profile-pic.jpg",
    "sameAs": [
      "https://www.linkedin.com/in/althafhussainsyed/",
      "https://github.com/ALTHAFHUSSAINSYED"
    ],
    "knowsAbout": [
      "DevOps Engineering",
      "Cloud Computing",
      "Amazon Web Services (AWS)",
      "Microsoft Azure",
      "Google Cloud Platform",
      "Kubernetes",
      "Docker",
      "CI/CD Pipelines",
      "Terraform",
      "Ansible",
      "Infrastructure as Code",
      "Site Reliability Engineering",
      "Microservices Architecture",
      "Container Orchestration",
      "GitOps",
      "Monitoring and Observability"
    ],
    "email": "mailto:althafhussainsyed@gmail.com",
    "alumniOf": {
      "@type": "CollegeOrUniversity",
      "name": "Maulana Azad National Institute of Technology"
    }
  };

  return (
    // ✨ MODIFIED: Added "relative" to create a stable anchor for the page layout.
    <div className="min-h-screen bg-background relative">
      <SEO
        title="Althaf Hussain | DevOps Engineer & Cloud Architect Portfolio"
        description="Certified AWS & Azure Cloud Solutions Architect with 3+ years of hands-on experience in DevOps automation, Kubernetes orchestration, and CI/CD pipeline development. Proven track record in infrastructure as code (Terraform, CloudFormation), microservices deployment, and cloud cost optimization. Browse 10+ real-world DevOps projects, technical blogs on AWS/Azure, and industry certifications. Based in India, available for remote DevOps consulting and full-time opportunities."
        keywords="DevOps Engineer, Cloud Architect, AWS Certified Solutions Architect, Azure DevOps, Kubernetes Expert, Docker, CI/CD Automation, Terraform, Ansible, Infrastructure as Code, Cloud Migration, Site Reliability Engineering, DevOps Portfolio, Cloud Native, Microservices, GitOps, Container Orchestration, Jenkins, GitHub Actions, AWS ECS, EKS, CloudFormation"
        url="https://althafportfolio.site"
        type="website"
        structuredData={homeStructuredData}
      />
      <HeroSection personalInfo={portfolioData.personal_info} />
      <AboutSection personalInfo={portfolioData.personal_info} achievements={portfolioData.achievements} education={portfolioData.education} />
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
