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
    try {
      const link = document.createElement('a');
      link.href = `${process.env.PUBLIC_URL || ''}/ALTHAF_HUSSAIN_SYED_DevOps_Resume.pdf`;
      link.download = 'Althaf_Hussain_Syed_DevOps_Resume.pdf';
      link.style.display = 'none';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      console.log('Resume download initiated');
    } catch (error) {
      console.error('Download error:', error);
      window.open(`${process.env.PUBLIC_URL || ''}/ALTHAF_HUSSAIN_SYED_DevOps_Resume.pdf`, '_blank');
    }
  };

  const scrollToContact = () => {
    const element = document.getElementById('contact');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section id="hero" className="bg-black py-20 lg:py-32 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
        
        {/* Floating particles */}
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-cyan-400 rounded-full floating opacity-20"></div>
        <div className="absolute top-3/4 right-1/4 w-1 h-1 bg-pink-500 rounded-full floating-reverse opacity-30"></div>
        <div className="absolute top-1/2 left-3/4 w-1.5 h-1.5 bg-green-400 rounded-full bounce-slow opacity-25"></div>
        <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-yellow-400 rounded-full floating opacity-20"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center max-w-4xl mx-auto">

          <div className={`relative flex justify-center items-center mb-8 w-full h-56 ${isVisible ? 'fade-in' : ''}`}>
            {/* Left Video */}
            <video 
              src="/videos/intro_left.mp4" 
              autoPlay 
              loop 
              muted 
              playsInline
              // 🔧 MODIFIED: Changed rounded-full to rounded-xl for a square/rectangle shape
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
              src="/videos/intro_right.mp4" 
              autoPlay 
              loop 
              muted
              playsInline
              // 🔧 MODIFIED: Changed rounded-full to rounded-xl for a square/rectangle shape
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
            <div className="flex items-center gap-2 hover:text-blue-soft transition-all
