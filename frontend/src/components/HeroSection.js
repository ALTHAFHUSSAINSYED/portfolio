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

          {/* === YOUR PROFILE IMAGE: Sizing Adjusted === */}
          <div className={`flex justify-center mb-8 ${isVisible ? 'fade-in' : ''}`}>
            <img 
              src="/profile-pic.jpg"
              alt={personalInfo.name}
              // Changed from w-40 h-40 to w-56 h-56 for a larger size
              // object-cover ensures it perfectly fills the circular frame without stretching
              className="w-56 h-56 rounded-full object-cover border-4 border-cyan-400/30 shadow-lg shadow-cyan-500/20"
            />
          </div>

          {/* Professional Badge */}
          <Badge 
            variant="outline" 
            className={`mb-6 text-cyan-soft border-cyan-400/30 bg-black/50 px-4 py-2 hover:bg-cyan-400/5 transition-colors backdrop-blur-sm hover-glow ${isVisible ? 'fade-in stagger-1' : ''}`}
          >
            <span className="animate-pulse mr-2 text-green-soft">●</span>
            Available for New Opportunities
          </Badge>

          {/* Main Heading */}
          <h1 className={`text-4xl md:text-6xl font-bold mb-6 leading-tight hero-title ${isVisible ? 'fade-in-up stagger-2' : ''}`}>
            {personalInfo.name}
          </h1>

          {/* Professional Title */}
          <div className={`text-xl md:text-2xl font-semibold mb-8 ${isVisible ? 'fade-in-up stagger-3' : ''}`}>
            <span className="text-cyan-soft">{personalInfo.title.split('|')[0]}</span>
            {personalInfo.title.includes('|') && (
              <span className="text-pink-soft"> | {personalInfo.title.split('|')[1]}</span>
            )}
          </div>

          {/* Summary */}
          <p className={`text-lg md:text-xl text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed ${isVisible ? 'fade-in-up stagger-4' : ''}`}>
            {personalInfo.summary}
          </p>

          {/* Contact Info Row */}
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
              <a 
                href={personalInfo.linkedin} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-sm font-medium hover:underline"
              >
                LinkedIn Profile
              </a>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className={`flex flex-col sm:flex-row gap-4 justify-center items-center ${isVisible ? 'fade-in-up stagger-6' : ''}`}>
            <Button
              onClick={downloadResume}
              size="lg"
              className="neon-button bg-gradient-to-r from-pink-500/80 to-cyan-400/80 hover:from-pink-500 hover:to-cyan-400 text-black px-8 py-3 text-lg font-bold transition-all duration-300"
            >
              <Download className="w-5 h-5 mr-3" />
              Download Resume
            </Button>
            <Button
              onClick={scrollToContact}
              variant="outline"
              size="lg"
              className="border-cyan-400/50 text-cyan-soft bg-black/50 hover:bg-cyan-400/10 hover:text-cyan-400 px-8 py-3 text-lg font-medium hover-lift transition-all duration-300 backdrop-blur-sm"
            >
              <Mail className="w-5 h-5 mr-3" />
              Get in Touch
            </Button>
          </div>

          {/* Key Stats */}
          <div className={`mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-2xl mx-auto ${isVisible ? 'slide-in-bottom stagger-7' : ''}`}>
            <div className="text-center p-6 bg-black/50 rounded-lg border border-cyan-400/10 hover:border-cyan-400/20 transition-all backdrop-blur-sm neon-card hover-lift">
              <div className="text-3xl font-bold text-cyan-soft mb-2 counter">3+</div>
              <div className="text-gray-300 font-medium">Years Experience</div>
            </div>
            <div className="text-center p-6 bg-black/50 rounded-lg border border-pink-500/10 hover:border-pink-500/20 transition-all backdrop-blur-sm neon-card hover-lift">
              <div className="text-3xl font-bold text-pink-soft mb-2 counter">14+</div>
              <div className="text-gray-300 font-medium">Certifications</div>
            </div>
            <div className="text-center p-6 bg-black/50 rounded-lg border border-green-400/10 hover:border-green-400/20 transition-all backdrop-blur-sm neon-card hover-lift">
              <div className="text-3xl font-bold text-green-soft mb-2 counter">99.9%</div>
              <div className="text-gray-300 font-medium">Uptime Achieved</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
