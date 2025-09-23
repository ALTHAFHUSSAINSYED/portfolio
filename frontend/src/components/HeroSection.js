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

  // Effect to handle play/pause on scroll
  useEffect(() => {
    const handleScroll = () => {
      const shouldPlay = window.scrollY < 300; // Play only when near the top of the page
      
      const manageVideo = (videoRef) => {
        if (videoRef.current) {
          if (shouldPlay && videoRef.current.paused) {
            videoRef.current.play().catch(error => console.log("Video autoplay prevented by browser."));
          } else if (!shouldPlay && !videoRef.current.paused) {
            videoRef.current.pause();
          }
        }
      };
      
      manageVideo(leftVideoRef.current);
      manageVideo(rightVideoRef.current);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    
    // Attempt to play videos on initial load after a short delay to ensure they are ready
    setTimeout(handleScroll, 500);

    return () => window.removeEventListener('scroll', handleScroll);
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
    <section id="hero" className="bg-black py-20 lg:py-32 relative overflow-hidden">
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
      
      <div className="absolute inset-0 overflow-hidden z-0">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Main container for the entire hero layout */}
        <div className="relative flex flex-col items-center">
        
          {/* Central Profile Picture */}
          <div className="relative z-20 mb-8">
            <img  
              src="/profile-pic.jpg"
              alt={personalInfo.name}
              className="w-48 h-48 md:w-56 md:h-56 rounded-full object-cover border-4 border-cyan-400/30 shadow-lg shadow-cyan-500/20"
            />
          </div>

          {/* SVG Container for Pipelines - positioned behind text but above videos */}
          <svg className="absolute top-0 left-0 w-full h-full z-10" viewBox="0 0 1200 800" preserveAspectRatio="xMidYMid meet">
            {/* Corrected Zig-Zag path to left video box */}
            <path d="M 600 112 C 400 250, 300 350, 200 500" stroke="url(#left-grad)" strokeWidth="4" fill="none" className="snake-path" />
            {/* Corrected Zig-Zag path to right video box */}
            <path d="M 600 112 C 800 250, 900 350, 1000 500" stroke="url(#right-grad)" strokeWidth="4" fill="none" className="snake-path" />
            <defs>
              <linearGradient id="left-grad"><stop offset="0%" stopColor="#22d3ee" /><stop offset="100%" stopColor="#ec4899" /></linearGradient>
              <linearGradient id="right-grad"><stop offset="0%" stopColor="#22d3ee" /><stop offset="100%" stopColor="#34d399" /></linearGradient>
            </defs>
          </svg>

          {/* Grid container for Text and Videos */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-center w-full mt-8">
            
            {/* Left Video - in the first grid column */}
            <div className="relative group z-20 hidden lg:flex justify-center">
              <video ref={leftVideoRef} src={`${process.env.PUBLIC_URL}/videos/intro_left.mp4`} playsInline loop muted className="w-72 h-72 rounded-xl object-cover border-2 border-pink-500/30 shadow-lg"></video>
              <button onClick={() => toggleMute(leftVideoRef, setIsLeftMuted)} className="absolute bottom-2 right-2 p-2 bg-black/50 rounded-full text-white">
                {isLeftMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
              </button>
            </div>
            
            {/* Main Text Content - in the central grid column */}
            <div className="relative text-center z-20">
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

            {/* Right Video - in the third grid column */}
            <div className="relative group z-20 hidden lg:flex justify-center">
               <video ref={rightVideoRef} src={`${process.env.PUBLIC_URL}/videos/intro_right.mp4`} playsInline loop muted className="w-72 h-72 rounded-xl object-cover border-2 border-green-500/30 shadow-lg"></video>
              <button onClick={() => toggleMute(rightVideoRef, setIsRightMuted)} className="absolute bottom-2 right-2 p-2 bg-black/50 rounded-full text-white">
                {isRightMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
              </button>
            </div>
            
             {/* Videos for smaller screens, displayed below the text */}
            <div className="lg:hidden col-span-1 flex justify-around items-center w-full mt-8">
                 <div className="relative group">
                    <video ref={leftVideoRef} src={`${process.env.PUBLIC_URL}/videos/intro_left.mp4`} playsInline loop muted className="w-48 h-48 rounded-xl object-cover border-2 border-pink-500/30 shadow-lg"></video>
                    <button onClick={() => toggleMute(leftVideoRef, setIsLeftMuted)} className="absolute bottom-2 right-2 p-2 bg-black/50 rounded-full text-white">
                        {isLeftMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
                    </button>
                </div>
                 <div className="relative group">
                    <video ref={rightVideoRef} src={`${process.env.PUBLIC_URL}/videos/intro_right.mp4`} playsInline loop muted className="w-48 h-48 rounded-xl object-cover border-2 border-green-500/30 shadow-lg"></video>
                    <button onClick={() => toggleMute(rightVideoRef, setIsRightMuted)} className="absolute bottom-2 right-2 p-2 bg-black/50 rounded-full text-white">
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

