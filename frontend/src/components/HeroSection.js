import React, { useEffect, useState, useRef } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Download, Mail, Linkedin, MapPin, Phone, Volume2, VolumeX } from 'lucide-react';

const HeroSection = ({ personalInfo }) => {
  const [isVisible, setIsVisible] = useState(false);
  const leftVideoRef = useRef(null);
  const rightVideoRef = useRef(null);
  const [isLeftMuted, setIsLeftMuted] = useState(true);
  const [isRightMuted, setIsRightMuted] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

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

  const toggleMute = (videoRef, setMutedState, isMutedState) => {
    if (videoRef.current) {
      const currentlyMuted = videoRef.current.muted;
      videoRef.current.muted = !currentlyMuted;
      setMutedState(!currentlyMuted);
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
          {/* Main content wrapper for positioning */}
          <div className="relative">
            <div className="flex justify-center items-center mb-8">
              <img
                src="/profile-pic.jpg"
                alt={personalInfo.name}
                className="relative z-10 w-56 h-56 rounded-full object-cover border-4 border-cyan-400/30 shadow-lg shadow-cyan-500/20"
              />
            </div>
            
            {/* Videos positioned absolutely relative to the main content wrapper */}
            {/* Left Video */}
            <div className="absolute top-0 -left-16 md:-left-8 lg:left-0 transform translate-y-4">
              <div className="relative group">
                <video 
                  ref={leftVideoRef}
                  src={`${process.env.PUBLIC_URL}/videos/intro_left.mp4`} 
                  autoPlay loop muted playsInline
                  className="w-52 h-52 rounded-xl object-cover border-2 border-pink-500/30 shadow-lg shadow-pink-500/20"
                ></video>
                <button 
                  onClick={() => toggleMute(leftVideoRef, setIsLeftMuted)}
                  className="absolute bottom-2 right-2 p-2 bg-black/50 rounded-full text-white transition-opacity"
                >
                  {isLeftMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
                </button>
              </div>
            </div>

            {/* Right Video */}
            <div className="absolute top-0 -right-16 md:-right-8 lg:right-0 transform translate-y-4">
               <div className="relative group">
                <video 
                  ref={rightVideoRef}
                  src={`${process.env.PUBLIC_URL}/videos/intro_right.mp4`} 
                  autoPlay loop muted playsInline
                  className="w-52 h-52 rounded-xl object-cover border-2 border-green-500/30 shadow-lg shadow-green-500/20"
                ></video>
                <button 
                  onClick={() => toggleMute(rightVideoRef, setIsRightMuted)}
                  className="absolute bottom-2 right-2 p-2 bg-black/50 rounded-full text-white transition-opacity"
                >
                  {isRightMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
                </button>
              </div>
            </div>
          </div>


          <Badge  
            variant="outline"  
            className={`mb-6 text-cyan-soft border-cyan-400/30 bg-black/50 px-4 py-2 ${isVisible ? 'fade-in stagger-1' : ''}`}
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
             {/* Contact Info */}
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

