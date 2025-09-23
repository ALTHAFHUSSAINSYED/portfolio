import React, { useEffect, useState, useRef } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Download, Mail, Volume2, VolumeX } from 'lucide-react';

const HeroSection = ({ personalInfo }) => {
  // Refs for video elements
  const leftVideoRef = useRef(null);
  const rightVideoRef = useRef(null);
  
  // State for mute toggles
  const [isLeftMuted, setIsLeftMuted] = useState(true);
  const [isRightMuted, setIsRightMuted] = useState(true);

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

  // Generic toggle mute function for either video
  const toggleMute = (videoRef, setMutedState) => {
    if (videoRef.current) {
      const isMuted = !videoRef.current.muted;
      videoRef.current.muted = isMuted;
      setMutedState(isMuted);
    }
  };

  return (
    <section id="hero" className="bg-black py-20 lg:py-32 relative overflow-hidden">
      {/* Inline style for SVG animation */}
      <style>{`
        @keyframes snake-draw {
          to { stroke-dashoffset: 0; }
        }
        .snake-path {
          stroke-dasharray: 1000;
          stroke-dashoffset: 1000;
          animation: snake-draw 8s linear infinite;
        }
      `}</style>
      
      {/* Background Orbs */}
      <div className="absolute inset-0 overflow-hidden z-0">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="relative flex flex-col items-center">
        
          {/* Central Profile Picture */}
          <div className="relative z-20 mb-8">
            <img  
              src="/profile-pic.jpg"
              alt={personalInfo.name}
              className="w-48 h-48 md:w-56 md:h-56 rounded-full object-cover border-4 border-cyan-400/30 shadow-lg shadow-cyan-500/20"
            />
          </div>

          {/* SVG Container for Pipelines */}
          <svg className="absolute top-0 left-0 w-full h-full z-10" viewBox="0 0 1200 800" preserveAspectRatio="xMidYMid meet">
            <path d="M 600 112 C 400 250, 300 350, 200 500" stroke="url(#left-grad)" strokeWidth="4" fill="none" className="snake-path" />
            <path d="M 600 112 C 800 250, 900 350, 1000 500" stroke="url(#right-grad)" strokeWidth="4" fill="none" className="snake-path" />
            <defs>
              <linearGradient id="left-grad"><stop offset="0%" stopColor="#22d3ee" /><stop offset="100%" stopColor="#ec4899" /></linearGradient>
              <linearGradient id="right-grad"><stop offset="0%" stopColor="#22d3ee" /><stop offset="100%" stopColor="#34d399" /></linearGradient>
            </defs>
          </svg>

          {/* REFACTORED Grid container for Text and Videos */}
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 lg:gap-16 items-center w-full mt-8">
            
            {/* Left Video */}
            <div className="z-20 order-2 lg:order-1 lg:col-span-1 flex justify-center lg:justify-start">
              <div className="relative group">
                <video 
                  ref={leftVideoRef} 
                  src="/videos/intro_left.mp4" 
                  autoPlay 
                  playsInline 
                  loop 
                  muted 
                  className="w-56 h-56 lg:w-72 lg:h-72 rounded-xl object-cover border-2 border-pink-500/30 shadow-lg"
                />
                <button onClick={() => toggleMute(leftVideoRef, setIsLeftMuted)} className="absolute bottom-2 right-2 p-2 bg-black/50 rounded-full text-white hover:bg-black/75 transition-colors">
                  {isLeftMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
                </button>
              </div>
            </div>

            {/* Main Text Content */}
            <div className="relative text-center z-20 order-1 lg:order-2 lg:col-span-3">
              <Badge variant="outline" className="mb-6"><span className="animate-pulse mr-2 text-green-soft">•</span>Available for New Opportunities</Badge>
              <h1 className="text-5xl md:text-7xl font-bold mb-6">{personalInfo.name}</h1>
              <div className="text-2xl md:text-3xl font-semibold mb-8">
                <span className="text-cyan-soft">{personalInfo.title.split('|')[0]}</span>
                {personalInfo.title.includes('|') && (<span className="text-pink-soft"> | {personalInfo.title.split('|')[1]}</span>)}
              </div>
              <p className="text-lg md:text-xl text-gray-300 mb-12 max-w-3xl mx-auto">{personalInfo.summary}</p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Button onClick={downloadResume} size="lg"><Download className="w-5 h-5 mr-3" />Download Resume</Button>
                <Button onClick={scrollToContact} variant="outline" size="lg"><Mail className="w-5 h-5 mr-3" />Get in Touch</Button>
              </div>
            </div>

            {/* Right Video */}
            <div className="z-20 order-3 lg:order-3 lg:col-span-1 flex justify-center lg:justify-end">
              <div className="relative group">
                <video 
                  ref={rightVideoRef} 
                  src="/videos/intro_right.mp4" 
                  autoPlay 
                  playsInline 
                  loop 
                  muted 
                  className="w-56 h-56 lg:w-72 lg:h-72 rounded-xl object-cover border-2 border-green-500/30 shadow-lg"
                />
                <button onClick={() => toggleMute(rightVideoRef, setIsRightMuted)} className="absolute bottom-2 right-2 p-2 bg-black/50 rounded-full text-white hover:bg-black/75 transition-colors">
                  {isRightMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
                </button>
              </div>
            </div>
            
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
