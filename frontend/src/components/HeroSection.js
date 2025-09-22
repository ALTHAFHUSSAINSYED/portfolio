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

  // ? NEW: Function to toggle mute state for a video
  const toggleMute = (videoRef, setMutedState) => {
    if (videoRef.current) {
      const isMuted = !videoRef.current.muted;
      videoRef.current.muted = isMuted;
      setMutedState(isMuted);
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
          <div className={`relative flex justify-center items-center mb-12 w-full`}>
            
            {/* ? MODIFIED: Left Video with new size, spacing, and mute button */}
            <div className="absolute left-0 top-1/2 -translate-y-1/2 md:left-auto md:-translate-x-56 group">
              <video 
                ref={leftVideoRef}
                src={`${process.env.PUBLIC_URL}/videos/intro_left.mp4`} 
                autoPlay loop muted playsInline
                className="w-48 h-48 md:w-52 md:h-52 rounded-xl object-cover border-2 border-pink-500/30 shadow-lg shadow-pink-500/20"
              ></video>
              <button 
                onClick={() => toggleMute(leftVideoRef, setIsLeftMuted)}
                className="absolute bottom-2 right-2 p-2 bg-black/50 rounded-full text-white opacity-0 group-hover:opacity-100 transition-opacity"
              >
                {isLeftMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
              </button>
            </div>
            
            <img  
              src="/profile-pic.jpg"
              alt={personalInfo.name}
              className="relative z-10 w-56 h-56 rounded-full object-cover border-4 border-cyan-400/30 shadow-lg shadow-cyan-500/20"
            />

            {/* ? MODIFIED: Right Video with new size, spacing, and mute button */}
            <div className="absolute right-0 top-1/2 -translate-y-1/2 md:right-auto md:translate-x-56 group">
              <video 
                ref={rightVideoRef}
                src={`${process.env.PUBLIC_URL}/videos/intro_right.mp4`} 
                autoPlay loop muted playsInline
                className="w-48 h-48 md:w-52 md:h-52 rounded-xl object-cover border-2 border-green-500/30 shadow-lg shadow-green-500/20"
              ></video>
              <button 
                onClick={() => toggleMute(rightVideoRef, setIsRightMuted)}
                className="absolute bottom-2 right-2 p-2 bg-black/50 rounded-full text-white opacity-0 group-hover:opacity-100 transition-opacity"
              >
                {isRightMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
              </button>
            </div>
          </div>

          {/* --- All other JSX code remains exactly the same --- */}
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
          
          {/* ... (rest of your component) ... */}

        </div>
      </div>
    </section>
  );
};

export default HeroSection;

