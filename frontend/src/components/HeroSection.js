import React, { useEffect, useState, useRef, useCallback } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Download, Mail, Volume2, VolumeX } from 'lucide-react';
import { LazyLoadImage } from 'react-lazy-load-image-component';
import 'react-lazy-load-image-component/src/effects/blur.css';

// A simple custom hook for media queries
const useMediaQuery = (query) => {
  const [matches, setMatches] = useState(false);
  useEffect(() => {
    const media = window.matchMedia(query);
    if (media.matches !== matches) {
      setMatches(media.matches);
    }
    const listener = () => setMatches(media.matches);
    media.addEventListener('change', listener);
    return () => media.removeEventListener('change', listener);
  }, [matches, query]);
  return matches;
};

const HeroSection = ({ personalInfo }) => {
  const leftVideoRef = useRef(null);
  const rightVideoRef = useRef(null);
  const bannerVideoRef = useRef(null); // Ref for the banner video

  const [isLeftMuted, setIsLeftMuted] = useState(true);
  const [isRightMuted, setIsRightMuted] = useState(true);
  const [isBannerMuted, setIsBannerMuted] = useState(true); // State for banner video mute
  const [profilePicLoaded, setProfilePicLoaded] = useState(false); // State to track profile pic load

  // Use useMediaQuery hook to check for large screens (Tailwind's 'lg' breakpoint)
  const isLargeScreen = useMediaQuery('(min-width: 1024px)');
  const isMobile = useMediaQuery('(max-width: 640px)');

  const handleVideoScroll = useCallback(() => {
    const videoElements = [leftVideoRef.current, rightVideoRef.current, bannerVideoRef.current];
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
    setTimeout(handleVideoScroll, 100);
    window.addEventListener('scroll', handleVideoScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleVideoScroll);
  }, [handleVideoScroll]);

  // Callback for when profile picture loads successfully
  const handleProfilePicLoad = () => {
    setProfilePicLoaded(true);
  };

  const downloadResume = () => {
    const link = document.createElement('a');
    link.href = '/AlthafResume.pdf';
    link.download = 'AlthafResume.pdf';
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
    // ✨ MODIFIED: Changed bg-black to bg-background. Reduced bottom padding to pull next section up.
    <section id="hero" className="bg-background pt-20 pb-10 lg:pt-32 lg:pb-14 relative overflow-hidden">
      <style>{`
        @keyframes snake-draw {
          to { stroke-dashoffset: 0; }
        }
        /* Conditionally apply animation based on profilePicLoaded state */
        .snake-path-animated {
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

      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="relative flex flex-col items-center">

          <div className="relative z-20 mb-8 w-48 h-48 md:w-56 md:h-56 rounded-full border-4 border-cyan-400/30 shadow-lg shadow-cyan-500/20 overflow-hidden group mx-auto">
            <LazyLoadImage
              src="/profile-pic.jpg?v=updated3"
              alt="Althaf Hussain Syed - DevOps Engineer and Cloud Infrastructure Engineer specializing in AWS, Azure, Kubernetes"
              effect="blur"
              afterLoad={handleProfilePicLoad}
              className="w-full h-full object-cover transform scale-125 transition-transform duration-500 group-hover:scale-135"
              style={isMobile ? { objectFit: 'cover', objectPosition: '15% 10%', transform: 'scale(1.28)' } : {}}
              width={224}
              height={224}
            />
          </div>

          {/* Conditionally render SVG only on large screens */}
          {isLargeScreen && (
            <svg className="absolute top-0 left-0 w-full h-full z-0 pointer-events-none" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid meet">
              {/* --- SVG PATHS UPDATED for top-center connection --- */}
              {/* Added conditional class for animation */}
              <path d="M 800 128 C 300 300, 200 400, 250 510" stroke="url(#left-grad)" strokeWidth="4" fill="none" className={profilePicLoaded ? "snake-path-animated" : ""} />
              <path d="M 800 128 C 1300 300, 1400 400, 1350 510" stroke="url(#right-grad)" strokeWidth="4" fill="none" className={profilePicLoaded ? "snake-path-animated" : ""} />
              <defs>
                <linearGradient id="left-grad">
                  <stop offset="0%" stopColor="#22d3ee" />
                  <stop offset="100%" stopColor="#ec4899" />
                </linearGradient>
                <linearGradient id="right-grad">
                  <stop offset="0%" stopColor="#22d3ee" />
                  <stop offset="100%" stopColor="#34d399" />
                </linearGradient>
              </defs>
            </svg>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 lg:gap-4 items-start w-full mt-8">

            <div className="relative z-30 order-2 lg:order-1 lg:col-span-1 flex justify-center lg:justify-start pt-4">
              <div className="relative group bg-background rounded-xl">
                <video
                  ref={leftVideoRef}
                  src="https://res.cloudinary.com/dtzaicj6s/video/upload/f_auto,q_auto/intro_left_sgbvmy.mp4"
                  autoPlay
                  playsInline
                  loop
                  muted={isLeftMuted}
                  className="w-72 h-96 lg:w-[500px] lg:h-80 rounded-xl object-cover object-top border-2 border-pink-500/30 shadow-lg"
                />
                {/* ✨ MODIFIED: Changed bg-black/50 to bg-background/50 and text-white to text-foreground */}
                <button onClick={() => toggleMute(leftVideoRef, setIsLeftMuted)} className="absolute bottom-2 right-2 p-2 bg-background/50 rounded-full text-foreground hover:bg-background/75 transition-colors">
                  {isLeftMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
                </button>
              </div>
            </div>

            <div className="relative text-center z-30 order-1 lg:order-2 lg:col-span-3">
              <Badge variant="outline" className="mb-6"><span className="animate-pulse mr-2 text-green-soft">•</span>Available for New Opportunities</Badge>
              <h1 className="text-5xl md:text-7xl font-bold mb-6">{personalInfo.name}</h1>
              <div className="text-2xl md:text-3xl font-semibold mb-8">
                <span className="text-cyan-soft">{personalInfo.title.split('|')[0]}</span>
                {personalInfo.title.includes('|') && (<span className="text-pink-soft"> | {personalInfo.title.split('|')[1]}</span>)}
              </div>

              {/* ✨ MODIFIED: Changed text-gray-300 to text-muted-foreground */}
              <p className="text-lg md:text-xl text-muted-foreground mb-12 max-w-3xl mx-auto">{personalInfo.heroSummary}</p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Button
                  onClick={downloadResume}
                  size="lg"
                  className="bg-gradient-to-r from-pink-500 to-green-500 text-white hover:from-pink-600 hover:to-pink-600 dark:from-cyan-500 dark:to-purple-500 dark:hover:from-cyan-600 dark:hover:to-purple-600 border-0"
                >
                  <Download className="w-5 h-5 mr-3" />Download Resume
                </Button>
                <Button
                  onClick={scrollToContact}
                  size="lg"
                  className="bg-gradient-to-r from-pink-500 to-green-500 text-white hover:from-pink-600 hover:to-pink-600 dark:from-cyan-500 dark:to-purple-500 dark:hover:from-cyan-600 dark:hover:to-purple-600 border-0"
                >
                  <Mail className="w-5 h-5 mr-3" />Get in Touch
                </Button>
              </div>


            </div>

            <div className="relative z-30 order-3 lg:order-3 lg:col-span-1 flex justify-center lg:justify-end pt-4">
              <div className="relative group bg-background rounded-xl">
                <video
                  ref={rightVideoRef}
                  src="https://res.cloudinary.com/dtzaicj6s/video/upload/f_auto,q_auto/intro_right_gaebz0.mp4"
                  autoPlay
                  playsInline
                  loop
                  muted={isRightMuted}
                  className="w-72 h-96 lg:w-[500px] lg:h-80 rounded-xl object-cover object-top border-2 border-green-500/30 shadow-lg"
                />
                {/* ✨ MODIFIED: Changed bg-black/50 to bg-background/50 and text-white to text-foreground */}
                <button onClick={() => toggleMute(rightVideoRef, setIsRightMuted)} className="absolute bottom-2 right-2 p-2 bg-background/50 rounded-full text-foreground hover:bg-background/75 transition-colors">
                  {isRightMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
                </button>
              </div>
            </div>

          </div>
        </div>

        {/* Profile Video Banner */}
        {/* ✨ MODIFIED: Increased top margin to mt-12 to push video down. */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
          <div className="relative overflow-hidden rounded-2xl shadow-2xl transform lg:scale-90 origin-center group">
            <video
              ref={bannerVideoRef}
              src="https://res.cloudinary.com/dtzaicj6s/video/upload/f_auto,q_auto/Linkdn_uc533k.mp4"
              autoPlay
              playsInline
              loop
              muted={isBannerMuted}
              className="w-full h-auto object-cover dark:opacity-90 dark:brightness-95"
            />
            {/* ✨ MODIFIED: Removed opacity classes to keep button always visible */}
            <button onClick={() => toggleMute(bannerVideoRef, setIsBannerMuted)} className="absolute bottom-4 right-4 p-3 bg-background/50 rounded-full text-foreground hover:bg-background/75 transition-colors duration-300">
              {isBannerMuted ? <VolumeX size={24} /> : <Volume2 size={24} />}
            </button>
          </div>
        </div>

      </div>
    </section>
  );
};

export default HeroSection;
