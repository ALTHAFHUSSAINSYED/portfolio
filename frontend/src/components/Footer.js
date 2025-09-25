import React, { useEffect, useRef, useState } from 'react';
import { Button } from './ui/button';
import { Linkedin, Mail, Phone, Download, ArrowUp } from 'lucide-react';

const Footer = ({ personalInfo }) => {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const downloadResume = () => {
    try {
      const link = document.createElement('a');
      link.href = `${process.env.PUBLIC_URL || ''}/ALTHAF_HUSSAIN_SYED_DevOps_Resume.pdf`;
      link.download = 'Althaf_Hussain_Syed_DevOps_Resume.pdf';
      link.style.display = 'none';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      console.log('Resume download initiated from footer');
    } catch (error) {
      console.error('Download error:', error);
      window.open(`${process.env.PUBLIC_URL || ''}/ALTHAF_HUSSAIN_SYED_DevOps_Resume.pdf`, '_blank');
    }
  };

  const currentYear = new Date().getFullYear();

  return (
    // ✨ MODIFIED: Uses theme-aware background and text colors
    <footer className="bg-secondary text-secondary-foreground py-12 relative overflow-hidden" ref={sectionRef}>
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="absolute top-1/4 right-1/5 w-3 h-3 bg-cyan-400/20 rounded-full floating opacity-30"></div>
        <div className="absolute bottom-1/3 left-1/4 w-2 h-2 bg-pink-500/20 rounded-full bounce-glow opacity-25"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* Personal Info */}
          <div className={`space-y-4 ${isVisible ? 'fade-in-left stagger-1' : ''}`}>
             {/* ✨ MODIFIED: Uses theme-aware text colors */}
            <h3 className="text-2xl font-bold text-foreground mb-4 shine-text-slow">
              {personalInfo.name}
            </h3>
            <p className="text-muted-foreground text-lg glow-text">
              {personalInfo.title}
            </p>
            <p className="text-muted-foreground leading-relaxed">
              Building scalable cloud infrastructure and DevOps solutions that drive business success.
            </p>
          </div>

          {/* Quick Links */}
          <div className={`space-y-4 ${isVisible ? 'fade-in-up stagger-2' : ''}`}>
             {/* ✨ MODIFIED: Uses theme-aware text colors */}
            <h4 className="text-lg font-semibold text-foreground mb-4 sparkle-text">
              Quick Links
            </h4>
            <div className="space-y-2">
              {[
                { id: 'about', name: 'About Me' },
                { id: 'skills', name: 'Technical Skills' },
                { id: 'experience', name: 'Experience' },
                { id: 'certifications', name: 'Certifications' },
                { id: 'contact', name: 'Contact' }
              ].map((link, index) => (
                <button 
                  key={link.id}
                  onClick={() => document.getElementById(link.id)?.scrollIntoView({ behavior: 'smooth' })}
                   // ✨ MODIFIED: Uses theme-aware text colors
                  className={`block text-muted-foreground hover:text-cyan-soft transition-all duration-300 text-left hover-glow glow-text nav-link ${
                    isVisible ? `fade-in-right stagger-${index + 3}` : ''
                  }`}
                >
                  {link.name}
                </button>
              ))}
            </div>
          </div>

          {/* Contact & Actions */}
          <div className={`space-y-4 ${isVisible ? 'fade-in-right stagger-3' : ''}`}>
             {/* ✨ MODIFIED: Uses theme-aware text colors */}
            <h4 className="text-lg font-semibold text-foreground mb-4 sparkle-text">
              Get in Touch
            </h4>
            
            {/* Contact Info */}
            <div className="space-y-3">
              <a 
                href={`mailto:${personalInfo.email}`}
                 // ✨ MODIFIED: Uses theme-aware text colors
                className="flex items-center space-x-3 text-muted-foreground hover:text-cyan-soft transition-all duration-300 hover-glow glow-text"
              >
                <Mail className="w-4 h-4 pulse-shine" />
                <span>{personalInfo.email}</span>
              </a>
              <a 
                href={`tel:${personalInfo.phone}`}
                 // ✨ MODIFIED: Uses theme-aware text colors
                className="flex items-center space-x-3 text-muted-foreground hover:text-green-soft transition-all duration-300 hover-glow glow-text"
              >
                <Phone className="w-4 h-4 pulse-shine" />
                <span>{personalInfo.phone}</span>
              </a>
              <a 
                href={personalInfo.linkedin}
                target="_blank"
                rel="noopener noreferrer"
                 // ✨ MODIFIED: Uses theme-aware text colors
                className="flex items-center space-x-3 text-muted-foreground hover:text-blue-soft transition-all duration-300 hover-glow glow-text"
              >
                <Linkedin className="w-4 h-4 pulse-shine" />
                <span>LinkedIn Profile</span>
              </a>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3 pt-4">
              <Button
                onClick={downloadResume}
                size="sm"
                className="w-full neon-button bg-gradient-to-r from-cyan-500/80 to-pink-500/80 hover:from-cyan-500 hover:to-pink-500 text-black transition-all duration-300"
              >
                <Download className="w-4 h-4 mr-2" />
                Download Resume
              </Button>
              <Button
                onClick={() => window.open(personalInfo.linkedin, '_blank')}
                variant="outline"
                size="sm"
                 // ✨ MODIFIED: Uses theme-aware background color
                className="w-full border-cyan-400/50 text-cyan-soft bg-background/50 hover:bg-cyan-400/10 hover:border-cyan-400 transition-all duration-300 backdrop-blur-sm hover-lift sparkle-text"
              >
                <Linkedin className="w-4 h-4 mr-2" />
                Connect on LinkedIn
              </Button>
            </div>
          </div>
        </div>

        {/* Divider */}
        {/* ✨ MODIFIED: Uses theme-aware border color */}
        <div className="border-t border-border/50 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            {/* Copyright */}
            <div className={`text-center md:text-left ${isVisible ? 'fade-in-up stagger-4' : ''}`}>
               {/* ✨ MODIFIED: Uses theme-aware text colors */}
              <p className="text-muted-foreground glow-text">
                © {currentYear} <span className="sparkle-text">{personalInfo.name}</span>. All rights reserved.
              </p>
              <p className="text-muted-foreground text-sm mt-1">
                Built with Passion • <span className="text-gradient-animate">Made with ❤️</span>
              </p>
            </div>

            {/* Availability Status */}
            <div className={`flex items-center space-x-4 ${isVisible ? 'fade-in-up stagger-5' : ''}`}>
              <div className="flex items-center space-x-2 hover-glow transition-all duration-300 p-2 rounded">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse pulse-shine"></div>
                 {/* ✨ MODIFIED: Uses theme-aware text colors */}
                <span className="text-muted-foreground text-sm font-medium glow-text">
                  Available for new opportunities
                </span>
              </div>
              
              {/* Back to Top */}
              <Button
                onClick={scrollToTop}
                variant="outline"
                size="sm"
                 // ✨ MODIFIED: Uses theme-aware background color
                className="border-cyan-400/50 text-cyan-soft bg-background/50 hover:bg-cyan-400/10 hover:border-cyan-400 transition-all duration-300 hover-lift sparkle-text"
              >
                <ArrowUp className="w-4 h-4 mr-2" />
                Back to Top
              </Button>
            </div>
          </div>
        </div>

        {/* Professional Statement */}
        <div className={`mt-8 text-center ${isVisible ? 'fade-in-up stagger-6' : ''}`}>
           {/* ✨ MODIFIED: Uses theme-aware text colors */}
          <p className="text-muted-foreground text-sm max-w-2xl mx-auto glow-text">
            Dedicated to delivering exceptional DevOps solutions that empower teams to build, 
            deploy, and scale applications with <span className="text-gradient-animate">confidence and reliability</span>.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
