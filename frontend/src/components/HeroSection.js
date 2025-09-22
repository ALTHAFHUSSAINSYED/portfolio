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

  // Effect for initial fade-in animation
  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  // ✨ FIXED: Effect to handle muting/unmuting on scroll
  useEffect(() => {
    const handleScroll = () => {
      const shouldMute = window.scrollY > 150; // Mute if scrolled down
      
      if (leftVideoRef.current && leftVideoRef.current.muted !== shouldMute) {
        leftVideoRef.current.muted = shouldMute;
        setIsLeftMuted(shouldMute);
      }
      if (rightVideoRef.current && rightVideoRef.current.muted !== shouldMute) {
        rightVideoRef.current.muted = shouldMute;
        setIsRightMuted(shouldMute);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    // Initial check in case the page loads scrolled down
    handleScroll(); 

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
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
      const isCurrentlyMuted = videoRef.current.muted;
      videoRef.current.muted = !isCurrentlyMuted;
      setMutedState(!isCurrentlyMuted);
    }
  };

  return (
    <section id="hero" className="bg-black pt-20 pb-12 lg:pt-32 lg:pb-24 relative overflow-hidden min-h-[700px] md:min-h-[800px]">
      <style>{`
        @keyframes snake {
          to { stroke-dashoffset: 0; }
        }
        .snake-pipeline {
          stroke-dasharray: 1000;
          stroke-dashoffset: 1000;
          animation: snake 6s linear infinite;
        }
      `}</style>
      
      <div className="absolute inset-0 overflow-hidden">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 h-full">
        {/* Container for Profile Pic, Videos, and Pipelines */}
        <div className="absolute top-0 left-0 w-full h-full">
            {/* Central Profile Picture */}
            <div className="absolute top-10 left-1/2 -translate-x-1/2 z-20">
              <img  
                src="/profile-pic.jpg"
                alt={personalInfo.name}
                className="w-48 h-48 md:w-56 md:h-56 rounded-full object-cover border-4 border-cyan-400/30 shadow-lg shadow-cyan-500/20"
              />
            </div>

            {/* ✨ FIXED: SVG Container for Pipelines with valid coordinates */}
            <svg className="absolute top-0 left-0 w-full h-full z-10" viewBox="0 0 1200 600" preserveAspectRatio="xMidYMid meet" style={{ filter: 'drop-shadow(0 0 5px rgba(0, 255, 255, 0.3))' }}>
              <path 
                d="M 600 112 C 400 150, 200 300, 120 450" 
                stroke="url(#left-gradient)" 
                strokeWidth="3" 
                fill="none" 
                className="snake-pipeline"
              />
              <path 
                d="M 600 112 C 800 150, 1000 300, 1080 450" 
                stroke="url(#right-gradient)" 
                strokeWidth="3" 
                fill="none" 
                className="snake-pipeline"
              />
              <defs>
                <linearGradient id="left-gradient"><stop offset="0%" stopColor="#22d3ee" /><stop offset="100%" stopColor="#ec4899" /></linearGradient>
                <linearGradient id="right-gradient"><stop offset="0%" stopColor="#22d3ee" /><stop offset="100%" stopColor="#34d399" /></linearGradient>
              </defs>
            </svg>

            {/* ✨ FIXED: Left Video Position */}
            <div className="absolute bottom-20 left-4 md:left-[10%] group z-20">
              <video ref={leftVideoRef} src={`${process.env.PUBLIC_URL}/videos/intro_left.mp4`} autoPlay loop playsInline muted className="w-48 h-48 md:w-56 md:h-56 rounded-xl object-cover border-2 border-pink-500/30 shadow-lg"></video>
              <button onClick={() => toggleMute(leftVideoRef, setIsLeftMuted)} className="absolute bottom-2 right-2 p-2 bg-black/50 rounded-full text-white">
                {isLeftMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
              </button>
            </div>

            {/* ✨ FIXED: Right Video Position */}
            <div className="absolute bottom-20 right-4 md:right-[10%] group z-20">
               <video ref={rightVideoRef} src={`${process.env.PUBLIC_URL}/videos/intro_right.mp4`} autoPlay loop playsInline muted className="w-48 h-48 md:w-56 md:h-56 rounded-xl object-cover border-2 border-green-500/30 shadow-lg"></video>
              <button onClick={() => toggleMute(rightVideoRef, setIsRightMuted)} className="absolute bottom-2 right-2 p-2 bg-black/50 rounded-full text-white">
                {isRightMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
              </button>
            </div>
        </div>
        
        {/* Text content is in a separate container to prevent overlap */}
        <div className="relative text-center pt-64 md:pt-72">
            <Badge variant="outline" className={`mb-6 text-cyan-soft border-cyan-400/30 bg-black/50 px-4 py-2`}>
              <span className="animate-pulse mr-2 text-green-soft">•</span> Available for New Opportunities
            </Badge>
            <h1 className={`text-4xl md:text-6xl font-bold mb-6`}>{personalInfo.name}</h1>
            <div className={`text-xl md:text-2xl font-semibold mb-8`}>
              <span className="text-cyan-soft">{personalInfo.title.split('|')[0]}</span>
              {personalInfo.title.includes('|') && (<span className="text-pink-soft"> | {personalInfo.title.split('|')[1]}</span>)}
            </div>
            <p className={`text-lg md:text-xl text-gray-300 mb-12 max-w-3xl mx-auto`}>{personalInfo.summary}</p>
            <div className={`flex flex-col sm:flex-row gap-4 justify-center items-center`}>
              <Button onClick={downloadResume} size="lg" className="w-full sm:w-auto neon-button bg-gradient-to-r from-pink-500 to-cyan-400 text-black font-bold"><Download className="w-5 h-5 mr-3" />Download Resume</Button>
              <Button onClick={scrollToContact} variant="outline" size="lg" className="w-full sm:w-auto border-cyan-400/50 text-cyan-soft bg-black/50 hover:bg-cyan-400/10"><Mail className="w-5 h-5 mr-3" />Get in Touch</Button>
            </div>
        </div>
      </div>
    </section>
  );
};
export default HeroSection;


