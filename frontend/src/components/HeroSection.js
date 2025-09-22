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

  useEffect(() => {
    const handleScroll = () => {
      const shouldMute = window.scrollY > 200;
      if (leftVideoRef.current) {
        leftVideoRef.current.muted = shouldMute;
        setIsLeftMuted(shouldMute);
      }
      if (rightVideoRef.current) {
        rightVideoRef.current.muted = shouldMute;
        setIsRightMuted(shouldMute);
      }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const downloadResume = () => { /* ... download logic ... */ };
  const scrollToContact = () => { /* ... scroll logic ... */ };

  const toggleMute = (videoRef, setMutedState) => {
    if (videoRef.current) {
      const isMuted = !videoRef.current.muted;
      videoRef.current.muted = isMuted;
      setMutedState(isMuted);
    }
  };

  return (
    <section id="hero" className="bg-black py-20 lg:py-32 relative overflow-hidden min-h-[850px]">
      <style>{`
        @keyframes snake-animation {
          to { stroke-dashoffset: 0; }
        }
        .snake-path {
          stroke-dasharray: 1000;
          stroke-dashoffset: 1000;
          animation: snake-animation 8s linear infinite;
        }
      `}</style>
      
      <div className="absolute inset-0 overflow-hidden">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="relative text-center">
          {/* Central Profile Picture */}
          <div className="relative inline-block z-20">
            <img  
              src="/profile-pic.jpg"
              alt={personalInfo.name}
              className="w-48 h-48 md:w-56 md:h-56 rounded-full object-cover border-4 border-cyan-400/30 shadow-lg shadow-cyan-500/20"
            />
          </div>
          
          {/* Animated SVG Pipelines */}
          <svg className="absolute top-0 left-0 w-full h-full z-10" viewBox="0 0 1200 600" preserveAspectRatio="none">
            {/* Zig-zag path to left video */}
            <path d="M 600 112 C 400 200, 300 250, 150 400" stroke="url(#left-grad)" strokeWidth="4" fill="none" className="snake-path" />
            {/* Zig-zag path to right video */}
            <path d="M 600 112 C 800 200, 900 250, 1050 400" stroke="url(#right-grad)" strokeWidth="4" fill="none" className="snake-path" />
            <defs>
              <linearGradient id="left-grad"><stop offset="0%" stopColor="#22d3ee" /><stop offset="100%" stopColor="#ec4899" /></linearGradient>
              <linearGradient id="right-grad"><stop offset="0%" stopColor="#22d3ee" /><stop offset="100%" stopColor="#34d399" /></linearGradient>
            </defs>
          </svg>
          
          {/* Main Content Area */}
          <div className="mt-8">
            <Badge variant="outline" className="mb-6"><span className="animate-pulse mr-2 text-green-soft">•</span>Available for New Opportunities</Badge>
            <h1 className="text-4xl md:text-6xl font-bold mb-6">{personalInfo.name}</h1>
            <div className="text-xl md:text-2xl font-semibold mb-8">
              <span className="text-cyan-soft">{personalInfo.title.split('|')[0]}</span>
              {personalInfo.title.includes('|') && (<span className="text-pink-soft"> | {personalInfo.title.split('|')[1]}</span>)}
            </div>
            <p className="text-lg md:text-xl text-gray-300 mb-12 max-w-3xl mx-auto">{personalInfo.summary}</p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button onClick={downloadResume} size="lg"><Download className="w-5 h-5 mr-3" />Download Resume</Button>
              <Button onClick={scrollToContact} variant="outline" size="lg"><Mail className="w-5 h-5 mr-3" />Get in Touch</Button>
            </div>
          </div>

          {/* Videos positioned at the corners */}
          <div className="absolute bottom-0 left-0 w-full h-full flex justify-between items-end z-20 pointer-events-none">
            <div className="pointer-events-auto">
              <video ref={leftVideoRef} src={`${process.env.PUBLIC_URL}/videos/intro_left.mp4`} autoPlay loop playsInline muted className="w-56 h-56 md:w-64 md:h-64 rounded-xl object-cover border-2 border-pink-500/30 shadow-lg"></video>
              <button onClick={() => toggleMute(leftVideoRef, setIsLeftMuted)} className="absolute bottom-2 right-2 p-2 bg-black/50 rounded-full text-white">
                {isLeftMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
              </button>
            </div>
            <div className="pointer-events-auto">
               <video ref={rightVideoRef} src={`${process.env.PUBLIC_URL}/videos/intro_right.mp4`} autoPlay loop playsInline muted className="w-56 h-56 md:w-64 md:h-64 rounded-xl object-cover border-2 border-green-500/30 shadow-lg"></video>
              <button onClick={() => toggleMute(rightVideoRef, setIsRightMuted)} className="absolute bottom-2 right-2 p-2 bg-black/50 rounded-full text-white">
                {isRightMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
              </button>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
};
export default HeroSection;


