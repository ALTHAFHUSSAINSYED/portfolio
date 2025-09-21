// src/components/HeroSection.js (Final Version)

import React, { useEffect, useState } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Download, Mail, Linkedin, MapPin, Phone } from 'lucide-react';

const HeroSection = ({ personalInfo }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  const downloadResume = () => {
    const resumeUrl = '/ALTHAF_HUSSAIN_SYED_DevOps_Resume.pdf';
    const link = document.createElement('a');
    link.href = resumeUrl;
    link.download = 'Althaf_Hussain_Syed_DevOps_Resume.pdf';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const scrollToContact = () => {
    document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section id="hero" className="bg-black py-20 lg:py-32 relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center max-w-4xl mx-auto">

          <div className={`relative flex justify-center items-center mb-8 w-full h-56 ${isVisible ? 'fade-in' : ''}`}>
            {/* Left Video */}
            <video 
              src="/videos/intro-left.mp4" 
              autoPlay loop muted playsInline
              className="absolute left-0 lg:left-1/4 transform -translate-x-1/2 lg:translate-x-0 w-48 h-48 rounded-xl object-cover border-2 border-pink-500/30 shadow-lg shadow-pink-500/20 opacity-0 animate-fade-in-left"
              style={{ animationDelay: '500ms' }}
            ></video>
            
            {/* Profile Image (Center) */}
            <img  
              src="/profile-pic.jpg"
              alt={personalInfo.name}
              className="relative z-10 w-56 h-56 rounded-full object-cover border-4 border-cyan-400/30 shadow-lg shadow-cyan-500/20"
            />

            {/* Right Video */}
            <video 
              src="/videos/intro-right.mp4" 
              autoPlay loop muted playsInline
              className="absolute right-0 lg:right-1/4 transform translate-x-1/2 lg:translate-x-0 w-48 h-48 rounded-xl object-cover border-2 border-green-500/30 shadow-lg shadow-green-500/20 opacity-0 animate-fade-in-right"
              style={{ animationDelay: '500ms' }}
            ></video>
          </div>

          <Badge  
            variant="outline"  
            className={`mb-6 text-cyan-soft border-cyan-400/30 bg-black/50 px-4 py-2 hover:bg-cyan-400/5 transition-colors backdrop-blur-sm hover-glow ${isVisible ? 'fade-in stagger-1' : ''}`}
          >
            <span className="animate-pulse mr-2 text-green-soft">•</span>
            Available for New Opportunities
          </Badge>

          <h1 className={`text-4xl md:text-6xl font-bold mb-6 leading-tight hero-title ${isVisible ? 'fade-in-up stagger-2' : ''}`}>
            {personalInfo.name}
          </h1>

          <div className={`text-xl md:text-2xl font-semibold mb-8 ${isVisible ? 'fade-in-up stagger-3' : ''}`}>
            <span className="text-cyan-soft">{personalInfo.title.split('|')[0]}</span>
            {personalInfo.title.includes('|') && (
              <span className="text-pink-soft"> | {personalInfo.title.split('|')[1]}</span>
            )}
          </div>
          
          <p className={`text-lg md:text-xl text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed ${isVisible ? 'fade-in-up stagger-4' : ''}`}>
            {personalInfo.summary}
          </p>

          {/* ... other sections like contact info and buttons remain the same ... */}
           <div className={`flex flex-wrap justify-center items-center gap-6 mb-12 text-gray-300 ${isVisible ? 'fade-in-up stagger-5' : ''}`}>
             <div className="flex items-center gap-2 hover:text-cyan-soft transition-all duration-300 hover-scale cursor-pointer">
               <MapPin className="w-4 h-4 text-cyan-soft" />
               <span className="text-sm font-medium">{personalInfo.location}</span>
             </div>
             <div className="flex items-center gap-2 hover:text-pink-soft transition-all duration-300 hover-scale">
               <Mail className="w-4 h-4 text-pink-soft" />
               <a href={`mailto:${personalInfo.email}`} className="text-sm font-medium hover:underline">
                 {personalInfo.email}
               </a>
             </div>
             <div className="flex items-center gap-2 hover:text-green-soft transition-all duration-300 hover-scale">
               <Phone className="w-4 h-4 text-green-soft" />
               <a href={`tel:${personalInfo.phone}`} className="text-sm font-medium hover:underline">
                 {personalInfo.phone}
               </a>
             </div>
             <div className="flex items-center gap-2 hover:text-blue-soft transition-all duration-300 hover-scale">
               <Linkedin className="w-4 h-4 text-blue-soft" />
               <a href={personalInfo.linkedin} target="_blank" rel="noopener noreferrer" className="text-sm font-medium hover:underline">
                 LinkedIn Profile
               </a>
             </div>
           </div>
           <div className={`flex flex-col sm:flex-row gap-4 justify-center items-center ${isVisible ? 'fade-in-up stagger-6' : ''}`}>
             <Button onClick={downloadResume} size="lg" className="neon-button bg-gradient-to-r from-pink-500/80 to-cyan-400/80 hover:from-pink-500 hover:to-cyan-400 text-black px-8 py-3 text-lg font-bold transition-all duration-300">
               <Download className="w-5 h-5 mr-3" />
               Download Resume
             </Button>
             <Button onClick={scrollToContact} variant="outline" size="lg" className="border-cyan-400/50 text-cyan-soft bg-black/50 hover:bg-cyan-400/10 hover:text-cyan-400 px-8 py-3 text-lg font-medium hover-lift transition-all duration-300 backdrop-blur-sm">
               <Mail className="w-5 h-5 mr-3" />
               Get in Touch
             </Button>
           </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
