import React, { useEffect, useState, useRef, useCallback } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Download, Mail, Volume2, VolumeX } from 'lucide-react';

const HeroSection = ({ personalInfo }) => {
  const leftVideoRef = useRef(null);
  const rightVideoRef = useRef(null);
  
  const [isLeftMuted, setIsLeftMuted] = useState(true);
  const [isRightMuted, setIsRightMuted] = useState(true);

  // Memoized function to handle video play/pause on scroll
  const handleVideoScroll = useCallback(() => {
    const videoElements = [leftVideoRef.current, rightVideoRef.current];
    // A lower threshold ensures the video is more fully in view before playing
    const threshold = 150; 

    videoElements.forEach((videoRef) => {
      if (videoRef) {
        const rect = videoRef.getBoundingClientRect();
        const isInView = (
          rect.top <= (window.innerHeight - threshold) &&
          rect.bottom >= threshold
        );

        if (isInView) {
          if (videoRef.paused) {
            videoRef.play().catch(error => {
              console.log("Video autoplay prevented by browser:", error);
            });
          }
        } else {
          if (!videoRef.paused) {
            videoRef.pause();
          }
        }
      }
    });
  }, []);

  useEffect(() => {
    // Initial check on mount
    setTimeout(handleVideoScroll, 100); // Small delay for videos to load
    window.addEventListener('scroll', handleVideoScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleVideoScroll);
  }, [handleVideoScroll]);

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
          stroke-dasharray: 1200;
          stroke-dashoffset: 1200;
          animation: snake-draw 8s linear infinite;
        }
      `}</style>
      
      <div className="absolute inset-0 overflow-hidden z-0">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="relative flex flex-col items-center">
        
          <div className="relative z-20 mb-8">
            <img  
              src="/profile-pic.jpg"
              alt={personalInfo.name}
              className="w-48 h-48 md:w-56 md:h-56 rounded-full object-cover border-4 border-cyan-400/30 shadow-lg shadow-cyan-500/20"
            />
          </div>

          {/* --- SVG PATHS UPDATED --- */}
          {/* viewBox, and path 'd' attributes were adjusted to widen the curves and reconnect to the top of the videos. */}
          <svg className="absolute top-0 left-0 w-full h-full z-10" viewBox="0 0 1400 900" preserveAspectRatio="xMidYMid meet">
            {/* Left path: Wider curve, connects to top of left video */}
            <path d="M 700 112 C 300 280, 250 420, 210 520" stroke="url(#left-grad)" strokeWidth="4" fill="none" className="snake-path" />
            {/* Right path: Wider curve, connects to top of right video */}
            <path d="M 700 112 C 1100 280, 1150 420, 1190 520" stroke="url(#right-grad)" strokeWidth="4" fill="none" className="snake-path" />
            <defs>
              <linearGradient id="left-grad"><stop offset="0%" stopColor="#22d3ee" /><stop offset="100%" stopColor="#ec4899" /></linearGradient>
              <linearGradient id="right-grad"><stop offset="0%" stopColor="#22d3ee" /><stop offset="100%" stopColor="#34d399" /></linearGradient>
            </defs>
          </svg>

          <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 lg:gap-16 items-start w-full mt-8">
            
            {/* --- VIDEO SIZE UPDATED --- */}
            {/* Left Video: Width increased to lg:w-96 */}
            <div className="z-20 order-2 lg:order-1 lg:col-span-1 flex justify-center lg:justify-start pt-12">
              <div className="relative group">
                <video 
                  ref={leftVideoRef} 
                  src="/videos/intro_left.mp4" 
                  autoPlay 
                  playsInline 
                  loop 
                  muted={isLeftMuted}
                  className="w-72 h-72 lg:w-96 lg:h-80 rounded-xl object-cover border-2 border-pink-500/30 shadow-lg"
                />
                <button onClick={() => toggleMute(leftVideoRef, setIsLeftMuted)} className="absolute bottom-2 right-2 p-2 bg-black/50 rounded-full text-white hover:bg-black/75 transition-colors">
                  {isLeftMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
                </button>
              </div>
            </div>

            {/* Main Text Content - Unchanged as requested */}
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

            {/* --- VIDEO SIZE UPDATED --- */}
            {/* Right Video: Width increased to lg:w-96 */}
            <div className="z-20 order-3 lg:order-3 lg:col-span-1 flex justify-center lg:justify-end pt-12">
              <div className="relative group">
                <video 
                  ref={rightVideoRef} 
                  src="/videos/intro_right.mp4" 
                  autoPlay 
                  playsInline 
                  loop 
                  muted={isRightMuted}
                  className="w-72 h-72 lg:w-96 lg:h-80 rounded-xl object-cover border-2 border-green-500/30 shadow-lg"
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
