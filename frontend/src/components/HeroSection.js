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

  const toggleMute = (videoRef, setMutedState) => {
    if (videoRef.current) {
      const isMuted = !videoRef.current.muted;
      videoRef.current.muted = isMuted;
      setMutedState(isMuted);
    }
  };

  return (
    <section id="hero" className="bg-black pt-20 pb-12 lg:pt-32 lg:pb-24 relative overflow-hidden">
      {/* Add CSS for the snake animation directly here */}
      <style>{`
        @keyframes snake {
          0% {
            stroke-dashoffset: 1000;
          }
          100% {
            stroke-dashoffset: 0;
          }
        }
        .snake-pipeline {
          stroke-dasharray: 1000;
          animation: snake 5s linear infinite;
        }
      `}</style>
      
      <div className="absolute inset-0 overflow-hidden">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center max-w-4xl mx-auto">
          
          {/* ✨ NEW: Container for the entire visual element */}
          <div className="relative w-full h-[450px] md:h-[500px] mb-8 flex justify-center items-start">
            {/* Central Profile Picture */}
            <img  
              src="/profile-pic.jpg"
              alt={personalInfo.name}
              className="relative z-20 w-56 h-56 rounded-full object-cover border-4 border-cyan-400/30 shadow-lg shadow-cyan-500/20"
            />

            {/* SVG Container for Pipelines */}
            <svg className="absolute top-0 left-0 w-full h-full z-10" style={{ filter: 'drop-shadow(0 0 5px rgba(0, 255, 255, 0.5))' }}>
              {/* Pipeline to Left Video */}
              <path 
                d="M 50% 112 Q 35% 200 20% 350" 
                stroke="url(#left-gradient)" 
                strokeWidth="3" 
                fill="none" 
                className="snake-pipeline"
              />
              {/* Pipeline to Right Video */}
              <path 
                d="M 50% 112 Q 65% 200 80% 350" 
                stroke="url(#right-gradient)" 
                strokeWidth="3" 
                fill="none" 
                className="snake-pipeline"
              />
              <defs>
                <linearGradient id="left-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style={{ stopColor: '#22d3ee' }} />
                  <stop offset="100%" style={{ stopColor: '#ec4899' }} />
                </linearGradient>
                <linearGradient id="right-gradient" x1="100%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" style={{ stopColor: '#22d3ee' }} />
                  <stop offset="100%" style={{ stopColor: '#34d399' }} />
                </linearGradient>
              </defs>
            </svg>

            {/* Left Video */}
            <div className="absolute top-[320px] left-[15%] md:left-[20%] transform -translate-x-1/2 group z-20">
              <video 
                ref={leftVideoRef}
                src={`${process.env.PUBLIC_URL}/videos/intro_left.mp4`} 
                autoPlay loop muted playsInline
                className="w-56 h-56 md:w-64 md:h-64 rounded-xl object-cover border-2 border-pink-500/30 shadow-lg shadow-pink-500/20 shadow-inner shadow-white/10"
              ></video>
              <button onClick={() => toggleMute(leftVideoRef, setIsLeftMuted)} className="absolute bottom-2 right-2 p-2 bg-black/50 rounded-full text-white"><VolumeX size={20} /></button>
            </div>

            {/* Right Video */}
            <div className="absolute top-[320px] right-[15%] md:right-[20%] transform translate-x-1/2 group z-20">
               <video 
                ref={rightVideoRef}
                src={`${process.env.PUBLIC_URL}/videos/intro_right.mp4`} 
                autoPlay loop muted playsInline
                className="w-56 h-56 md:w-64 md:h-64 rounded-xl object-cover border-2 border-green-500/30 shadow-lg shadow-green-500/20 shadow-inner shadow-white/10"
              ></video>
              <button onClick={() => toggleMute(rightVideoRef, setIsRightMuted)} className="absolute bottom-2 right-2 p-2 bg-black/50 rounded-full text-white"><VolumeX size={20} /></button>
            </div>
          </div>

          {/* Text content starts after the visual section */}
          <Badge variant="outline" className={`mb-6 text-cyan-soft border-cyan-400/30 bg-black/50 px-4 py-2 ${isVisible ? 'fade-in stagger-1' : ''}`}>
            <span className="animate-pulse mr-2 text-green-soft">•</span> Available for New Opportunities
          </Badge>
          <h1 className={`text-4xl md:text-6xl font-bold mb-6 ${isVisible ? 'fade-in-up stagger-2' : ''}`}>{personalInfo.name}</h1>
          <div className={`text-xl md:text-2xl font-semibold mb-8 ${isVisible ? 'fade-in-up stagger-3' : ''}`}>
            <span className="text-cyan-soft">{personalInfo.title.split('|')[0]}</span>
            {personalInfo.title.includes('|') && (<span className="text-pink-soft"> | {personalInfo.title.split('|')[1]}</span>)}
          </div>
          <p className={`text-lg md:text-xl text-gray-300 mb-12 max-w-3xl mx-auto ${isVisible ? 'fade-in-up stagger-4' : ''}`}>{personalInfo.summary}</p>
          <div className={`flex flex-col sm:flex-row gap-4 justify-center items-center ${isVisible ? 'fade-in-up stagger-6' : ''}`}>
            <Button onClick={downloadResume} size="lg" className="w-full sm:w-auto neon-button bg-gradient-to-r from-pink-500 to-cyan-400 text-black font-bold"><Download className="w-5 h-5 mr-3" />Download Resume</Button>
            <Button onClick={scrollToContact} variant="outline" size="lg" className="w-full sm:w-auto border-cyan-400/50 text-cyan-soft bg-black/50 hover:bg-cyan-400/10"><Mail className="w-5 h-5 mr-3" />Get in Touch</Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;

