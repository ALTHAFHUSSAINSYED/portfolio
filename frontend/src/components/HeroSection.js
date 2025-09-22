import React, { useEffect, useState, useRef } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Download, Mail, Linkedin, MapPin, Phone } from 'lucide-react';

const HeroSection = ({ personalInfo }) => {
  const [isVisible, setIsVisible] = useState(false);
  const leftVideoRef = useRef(null);
  const rightVideoRef = useRef(null);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  // --- All your other functions remain untouched ---
  const downloadResume = () => {
    const link = document.createElement('a');
    link.href = '/ALTHAF_HUSSAIN_SYED_DevOps_Resume.pdf';
    link.download = 'Althaf_Hussain_Syed_DevOps_Resume.pdf';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const scrollToContact = () => {
    document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleVideoHover = (videoRef) => {
    if (videoRef.current) {
      videoRef.current.muted = false;
    }
  };

  const handleVideoLeave = (videoRef) => {
    if (videoRef.current) {
      videoRef.current.muted = true;
    }
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
              ref={leftVideoRef}
              // ✨ CORRECTED: Ensured the path uses your confirmed filenames
              src={`${process.env.PUBLIC_URL}/videos/intro_left.mp4`} 
              autoPlay loop muted playsInline
              onMouseEnter={() => handleVideoHover(leftVideoRef)}
              onMouseLeave={() => handleVideoLeave(leftVideoRef)}
              className="absolute left-0 lg:left-1/4 transform -translate-x-1/2 lg:translate-x-0 w-48 h-48 rounded-xl object-cover border-2 border-pink-500/30 shadow-lg shadow-pink-500/20 cursor-pointer"
            ></video>
            
            <img  
              src="/profile-pic.jpg"
              alt={personalInfo.name}
              className="relative z-10 w-56 h-56 rounded-full object-cover border-4 border-cyan-400/30 shadow-lg shadow-cyan-500/20"
            />

            {/* Right Video */}
            <video 
              ref={rightVideoRef}
              // ✨ CORRECTED: Ensured the path uses your confirmed filenames
              src={`${process.env.PUBLIC_URL}/videos/intro_right.mp4`} 
              autoPlay loop muted playsInline
              onMouseEnter={() => handleVideoHover(rightVideoRef)}
              onMouseLeave={() => handleVideoLeave(rightVideoRef)}
              className="absolute right-0 lg:right-1/4 transform translate-x-1/2 lg:translate-x-0 w-48 h-48 rounded-xl object-cover border-2 border-green-500/30 shadow-lg shadow-green-500/20 cursor-pointer"
            ></video>
          </div>

          {/* --- All other JSX code for your name, title, buttons, etc. remains exactly the same --- */}
          <Badge  
            variant="outline"  
            className={`mb-6 text-cyan-soft border-cyan-400/30 bg-black/50 px-4 py-2 hover:bg-cyan-400/5 transition-colors ${isVisible ? 'fade-in stagger-1' : ''}`}
          >
            <span className="animate-pulse mr-2 text-green-soft">•</span>
            Available for New Opportunities
          </Badge>

          <h1 className={`text-4xl md:text-6xl font-bold mb-6 ${isVisible ? 'fade-in-up stagger-2' : ''}`}>
            {personalInfo.name}
          </h1>

          <div className={`text-xl md:text-2xl font-semibold mb-8 ${isVisible ? 'fade-in-up stagger-3' : ''}`}>
            <span className="text-cyan-soft">{personalInfo.title.split('|')[0]}</span>
            {personalInfo.title.includes('|') && (
              <span className="text-pink-soft"> | {personalInfo.title.split('|')[1]}</span>
            )}
          </div>
          
          <p className={`text-lg md:text-xl text-gray-300 mb-12 max-w-3xl mx-auto ${isVisible ? 'fade-in-up stagger-4' : ''}`}>
            {personalInfo.summary}
          </p>

           <div className={`flex flex-wrap justify-center items-center gap-6 mb-12 text-gray-300 ${isVisible ? 'fade-in-up stagger-5' : ''}`}>
             <div className="flex items-center gap-2"><MapPin className="w-4 h-4 text-cyan-soft" /><span>{personalInfo.location}</span></div>
             <div className="flex items-center gap-2"><Mail className="w-4 h-4 text-pink-soft" /><a href={`mailto:${personalInfo.email}`} className="hover:underline">{personalInfo.email}</a></div>
             <div className="flex items-center gap-2"><Phone className="w-4 h-4 text-green-soft" /><a href={`tel:${personalInfo.phone}`} className="hover:underline">{personalInfo.phone}</a></div>
             <div className="flex items-center gap-2"><Linkedin className="w-4 h-4 text-blue-soft" /><a href={personalInfo.linkedin} target="_blank" rel="noopener noreferrer" className="hover:underline">LinkedIn Profile</a></div>
           </div>
           <div className={`flex flex-col sm:flex-row gap-4 justify-center items-center ${isVisible ? 'fade-in-up stagger-6' : ''}`}>
             <Button onClick={downloadResume} size="lg" className="w-full sm:w-auto neon-button bg-gradient-to-r from-pink-500 to-cyan-400 text-black font-bold">
               <Download className="w-5 h-5 mr-3" />Download Resume
             </Button>
             <Button onClick={scrollToContact} variant="outline" size="lg" className="w-full sm:w-auto border-cyan-400/50 text-cyan-soft bg-black/50 hover:bg-cyan-400/10">
               <Mail className="w-5 h-5 mr-3" />Get in Touch
             </Button>
           </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;

