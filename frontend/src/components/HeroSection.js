// HeroSection.jsx
import React, { useEffect, useState, useRef, useCallback } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Download, Mail, Linkedin, MapPin, Phone } from 'lucide-react';

const HeroSection = ({ personalInfo }) => {
  const [isVisible, setIsVisible] = useState(false);

  // refs for DOM elements used to compute svg paths
  const containerRef = useRef(null);
  const profileRef = useRef(null);
  const leftVideoRef = useRef(null);
  const rightVideoRef = useRef(null);

  // dynamic SVG path d attributes
  const [leftPathD, setLeftPathD] = useState('');
  const [rightPathD, setRightPathD] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  // download resume
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

  // hover handlers: unmute on enter, mute on leave
  const handleVideoHover = (videoRef) => {
    if (videoRef?.current) {
      // some browsers require play() to be called explicitly to unmute
      videoRef.current.muted = false;
      const p = videoRef.current.play();
      if (p && typeof p.catch === 'function') p.catch(() => {});
    }
  };

  const handleVideoLeave = (videoRef) => {
    if (videoRef?.current) {
      videoRef.current.muted = true;
    }
  };

  // IntersectionObserver for play/pause based on visibility
  useEffect(() => {
    const options = { threshold: [0, 0.25, 0.5] };

    const observerCallback = (entries) => {
      entries.forEach(entry => {
        const vid = entry.target;
        if (!(vid instanceof HTMLVideoElement)) return;

        if (entry.intersectionRatio >= 0.25) {
          // play when at least 25% visible, keep muted by default
          if (vid.paused) {
            const p = vid.play();
            if (p && typeof p.catch === 'function') p.catch(() => {});
          }
          vid.muted = true; // keep muted unless hover
        } else {
          // pause & mute when not visible enough
          vid.pause();
          vid.muted = true;
        }
      });
    };

    const observer = new IntersectionObserver(observerCallback, options);

    if (leftVideoRef.current) observer.observe(leftVideoRef.current);
    if (rightVideoRef.current) observer.observe(rightVideoRef.current);

    return () => {
      observer.disconnect();
    };
  }, []);

  // helper to compute a smooth cubic bezier path between two DOM rect centers
  const computeCurvePath = (fromRect, toRect, svgRect, direction = 'left') => {
    if (!fromRect || !toRect || !svgRect) return '';

    // convert page coords into SVG local coords (svgRect is boundingClientRect of svg container)
    const startX = fromRect.left + fromRect.width / 2 - svgRect.left;
    const startY = fromRect.top + fromRect.height / 2 - svgRect.top;
    const endX = toRect.left + toRect.width / 2 - svgRect.left;
    const endY = toRect.top + toRect.height / 2 - svgRect.top;

    // choose control points for a nice curving arc. Control points are offset horizontally and vertically.
    const dx = Math.abs(endX - startX);
    const dy = Math.abs(endY - startY);
    const curvature = Math.max(80, dx * 0.5); // tweak curvature based on distance

    // control points push outwards left or right depending on which side
    const cp1x = startX + (direction === 'left' ? -curvature : curvature);
    const cp1y = startY - Math.max(20, dy * 0.2);

    const cp2x = endX + (direction === 'left' ? -curvature * 0.2 : curvature * 0.2);
    const cp2y = endY + Math.max(20, dy * 0.2);

    // return cubic bezier path
    return `M ${startX} ${startY} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${endX} ${endY}`;
  };

  // compute both path D attributes on resize/scroll
  const updatePaths = useCallback(() => {
    const svgEl = containerRef.current?.querySelector('svg.pipelines-svg');
    if (!svgEl || !profileRef.current || !leftVideoRef.current || !rightVideoRef.current) return;

    const svgRect = svgEl.getBoundingClientRect();
    const profileRect = profileRef.current.getBoundingClientRect();
    const leftRect = leftVideoRef.current.getBoundingClientRect();
    const rightRect = rightVideoRef.current.getBoundingClientRect();

    const leftD = computeCurvePath(profileRect, leftRect, svgRect, 'left');
    const rightD = computeCurvePath(profileRect, rightRect, svgRect, 'right');

    setLeftPathD(leftD);
    setRightPathD(rightD);
  }, []);

  useEffect(() => {
    // initial compute & listeners
    updatePaths();
    const ro = new ResizeObserver(() => updatePaths());
    if (containerRef.current) ro.observe(containerRef.current);

    window.addEventListener('scroll', updatePaths, { passive: true });
    window.addEventListener('resize', updatePaths);

    return () => {
      ro.disconnect();
      window.removeEventListener('scroll', updatePaths);
      window.removeEventListener('resize', updatePaths);
    };
  }, [updatePaths]);

  // small helper for video attributes to maximize autoplay reliability
  const commonVideoProps = {
    playsInline: true,
    preload: 'metadata',
    // autoPlay kept - will be controlled by IntersectionObserver
    autoPlay: true,
    loop: true,
  };

  return (
    <section id="hero" className="bg-black py-20 lg:py-32 relative overflow-hidden">
      {/* Inline styles for the pipeline animation & small utilities */}
      <style>{`
        /* "snake" stroke animation */
        .pipeline-path {
          stroke-width: 4;
          stroke-linecap: round;
          fill: none;
          stroke-dasharray: 140;
          stroke-dashoffset: 140;
          animation: dash 3s linear infinite;
        }
        @keyframes dash {
          from { stroke-dashoffset: 140; }
          to   { stroke-dashoffset: 0; }
        }
        /* subtle glow for pipeline */
        .pipeline-glow {
          filter: drop-shadow(0 4px 10px rgba(0,0,0,0.6));
        }

        /* fade-in helpers (you can also keep your existing classes) */
        .fade-in { opacity: 1; transform: none; transition: opacity .6s ease, transform .6s ease; }
        .fade-in-up { opacity: 1; transform: translateY(0); transition: opacity .6s ease, transform .6s ease; }
        .stagger-1 { transition-delay: .05s; } .stagger-2 { transition-delay: .12s; } .stagger-3 { transition-delay: .22s; } .stagger-4 { transition-delay: .32s; } .stagger-5 { transition-delay: .42s; } .stagger-6 { transition-delay: .52s; }
        .fade-in-up { opacity: 0; transform: translateY(16px); }
        .fade-in { opacity: 0; transform: scale(.98); }

        /* ensure video controls not visible but cursor pointer on hover */
        .video-card { cursor: pointer; }
      `}</style>

      <div className="absolute inset-0 overflow-hidden">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
      </div>

      <div ref={containerRef} className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center max-w-4xl mx-auto relative">

          {/* SVG overlay for pipelines — position absolute so it can draw across the block */}
          <svg className="pipelines-svg absolute left-0 top-0 w-full h-64 pointer-events-none" preserveAspectRatio="none">
            <defs>
              <linearGradient id="gradLeft" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#a78bfa" /> 
                <stop offset="100%" stopColor="#06b6d4" />
              </linearGradient>
              <linearGradient id="gradRight" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#06b6d4" />
                <stop offset="100%" stopColor="#fb7185" />
              </linearGradient>
            </defs>

            {/* left pipeline */}
            <path
              d={leftPathD}
              stroke="url(#gradLeft)"
              className="pipeline-path pipeline-glow"
              strokeOpacity="0.95"
            />

            {/* right pipeline */}
            <path
              d={rightPathD}
              stroke="url(#gradRight)"
              className="pipeline-path pipeline-glow"
              strokeOpacity="0.95"
            />
          </svg>

          {/* Main row: left video, profile, right video */}
          <div className={`relative flex items-center justify-center mb-8 w-full h-56 ${isVisible ? 'fade-in' : ''}`}>

            {/* Left Video — placed visually to the left corner */}
            <div
              className="absolute left-6 lg:left-8 transform -translate-y-1/2 top-1/2 w-48 h-48 rounded-xl overflow-hidden border-2 border-pink-500/20 shadow-lg shadow-pink-500/20 bg-black video-card"
              style={{ zIndex: 8 }}
            >
              <video
                {...commonVideoProps}
                ref={leftVideoRef}
                src={`${process.env.PUBLIC_URL}/videos/intro_left.mp4`}
                muted
                onMouseEnter={() => handleVideoHover(leftVideoRef)}
                onMouseLeave={() => handleVideoLeave(leftVideoRef)}
                className="w-full h-full object-cover"
              />
            </div>

            {/* Profile Image center */}
            <div style={{ zIndex: 12 }} className="relative">
              <img
                ref={profileRef}
                src="/profile-pic.jpg"
                alt={personalInfo?.name ?? 'Profile'}
                className="relative z-10 w-56 h-56 rounded-full object-cover border-4 border-cyan-400/30 shadow-lg shadow-cyan-500/20"
              />
            </div>

            {/* Right Video — placed visually to the right corner */}
            <div
              className="absolute right-6 lg:right-8 transform -translate-y-1/2 top-1/2 w-48 h-48 rounded-xl overflow-hidden border-2 border-green-500/20 shadow-lg shadow-green-500/20 bg-black video-card"
              style={{ zIndex: 8 }}
            >
              <video
                {...commonVideoProps}
                ref={rightVideoRef}
                src={`${process.env.PUBLIC_URL}/videos/intro_right.mp4`}
                muted
                onMouseEnter={() => handleVideoHover(rightVideoRef)}
                onMouseLeave={() => handleVideoLeave(rightVideoRef)}
                className="w-full h-full object-cover"
              />
            </div>
          </div>

          {/* --- The rest of your content (badge, name, title, summary, contacts, buttons) --- */}
          <Badge
            variant="outline"
            className={`mb-6 text-cyan-soft border-cyan-400/30 bg-black/50 px-4 py-2 hover:bg-cyan-400/5 transition-colors ${isVisible ? 'fade-in stagger-1' : ''}`}
            >
            <span className="animate-pulse mr-2 text-green-soft">•</span>
            Available for New Opportunities
          </Badge>

          <h1 className={`text-4xl md:text-6xl font-bold mb-6 ${isVisible ? 'fade-in-up stagger-2' : ''}`}>
            {personalInfo?.name}
          </h1>

          <div className={`text-xl md:text-2xl font-semibold mb-8 ${isVisible ? 'fade-in-up stagger-3' : ''}`}>
            <span className="text-cyan-soft">{personalInfo?.title?.split('|')?.[0]}</span>
            {personalInfo?.title?.includes('|') && (
              <span className="text-pink-soft"> | {personalInfo?.title?.split('|')?.[1]}</span>
            )}
          </div>

          <p className={`text-lg md:text-xl text-gray-300 mb-12 max-w-3xl mx-auto ${isVisible ? 'fade-in-up stagger-4' : ''}`}>
            {personalInfo?.summary}
          </p>

          <div className={`flex flex-wrap justify-center items-center gap-6 mb-12 text-gray-300 ${isVisible ? 'fade-in-up stagger-5' : ''}`}>
            <div className="flex items-center gap-2"><MapPin className="w-4 h-4 text-cyan-soft" /><span>{personalInfo?.location}</span></div>
            <div className="flex items-center gap-2"><Mail className="w-4 h-4 text-pink-soft" /><a href={`mailto:${personalInfo?.email}`} className="hover:underline">{personalInfo?.email}</a></div>
            <div className="flex items-center gap-2"><Phone className="w-4 h-4 text-green-soft" /><a href={`tel:${personalInfo?.phone}`} className="hover:underline">{personalInfo?.phone}</a></div>
            <div className="flex items-center gap-2"><Linkedin className="w-4 h-4 text-blue-soft" /><a href={personalInfo?.linkedin} target="_blank" rel="noopener noreferrer" className="hover:underline">LinkedIn Profile</a></div>
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
