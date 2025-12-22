import React, { useState, useEffect, useRef } from "react";
import { Download, Mail, Volume2, VolumeX } from "lucide-react";
import portfolioData from "../data/portfolio_data.json";
const personalInfo = portfolioData.personal_info;
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const HeroSection = () => {
  const [isLeftMuted, setIsLeftMuted] = useState(true);
  const [isRightMuted, setIsRightMuted] = useState(true);

  // Refs for dynamic line calculation
  const containerRef = useRef(null);
  const avatarRef = useRef(null);
  const leftVideoWrapperRef = useRef(null);
  const rightVideoWrapperRef = useRef(null);
  const [svgPaths, setSvgPaths] = useState({ left: "", right: "" });
  const [isMounted, setIsMounted] = useState(false);

  const leftVideoRef = useRef(null);
  const rightVideoRef = useRef(null);

  const toggleMute = (videoRef, setMuteState) => {
    if (videoRef.current) {
      videoRef.current.muted = !videoRef.current.muted;
      setMuteState(videoRef.current.muted);
    }
  };

  const handleVideoScroll = () => {
    [leftVideoRef, rightVideoRef].forEach((ref) => {
      if (ref.current) {
        const rect = ref.current.getBoundingClientRect();
        const isVisible = rect.top >= 0 && rect.bottom <= window.innerHeight;
        if (isVisible) {
          ref.current.play().catch(() => { });
        } else {
          ref.current.pause();
        }
      }
    });
  };

  // Dynamic Line Calculation
  const updatePaths = () => {
    if (!containerRef.current || !avatarRef.current || !leftVideoWrapperRef.current || !rightVideoWrapperRef.current) return;

    const containerRect = containerRef.current.getBoundingClientRect();
    const avatarRect = avatarRef.current.getBoundingClientRect();
    const leftRect = leftVideoWrapperRef.current.getBoundingClientRect();
    const rightRect = rightVideoWrapperRef.current.getBoundingClientRect();

    // Calculate generic relative coordinates
    const getRelativeCenter = (rect) => ({
      x: rect.left + rect.width / 2 - containerRect.left,
      y: rect.top + rect.height / 2 - containerRect.top,
    });

    // Avatar Bottom Center
    const avatarPoint = {
      x: avatarRect.left + avatarRect.width / 2 - containerRect.left,
      y: avatarRect.bottom - containerRect.top - 20 // Move up slightly to tuck behind
    };

    // Left Video Top Center
    const leftVideoPoint = {
      x: leftRect.left + leftRect.width / 2 - containerRect.left,
      y: leftRect.top - containerRect.top + 5 // Move down slightly to overlap
    };

    // Right Video Top Center
    const rightVideoPoint = {
      x: rightRect.left + rightRect.width / 2 - containerRect.left,
      y: rightRect.top - containerRect.top + 5 // Move down slightly to overlap
    };

    // Control Points for smooth Bezier curves
    // The control point pulls the line down/out. 
    // For left: Pull horizontally towards the video, then vertically down
    const leftControl = {
      x1: avatarPoint.x - (avatarPoint.x - leftVideoPoint.x) * 0.1, // Start vertical-ish
      y1: avatarPoint.y + (leftVideoPoint.y - avatarPoint.y) * 0.5,
      x2: leftVideoPoint.x + (avatarPoint.x - leftVideoPoint.x) * 0.1, // End entering from top
      y2: leftVideoPoint.y - (leftVideoPoint.y - avatarPoint.y) * 0.5,
    };

    // Simplified logic: Just use simple cubic bezier
    // M start C cp1x cp1y, cp2x cp2y, endx endy
    const curvature = 0.5; // Adjust for "hung" look

    // Left Path
    const leftPath = `
      M ${avatarPoint.x} ${avatarPoint.y} 
      C ${avatarPoint.x - 50} ${avatarPoint.y + 50}, 
        ${leftVideoPoint.x} ${leftVideoPoint.y - 100}, 
        ${leftVideoPoint.x} ${leftVideoPoint.y}
    `;

    // Right Path
    const rightPath = `
      M ${avatarPoint.x} ${avatarPoint.y} 
      C ${avatarPoint.x + 50} ${avatarPoint.y + 50}, 
        ${rightVideoPoint.x} ${rightVideoPoint.y - 100}, 
        ${rightVideoPoint.x} ${rightVideoPoint.y}
    `;

    setSvgPaths({ left: leftPath, right: rightPath });
  };

  useEffect(() => {
    setIsMounted(true);
    window.addEventListener("scroll", handleVideoScroll);
    window.addEventListener("resize", updatePaths);

    // Initial calculation (delay slightly to ensure layout is stable)
    if (isMounted) {
      setTimeout(updatePaths, 100);
    }

    return () => {
      window.removeEventListener("scroll", handleVideoScroll);
      window.removeEventListener("resize", updatePaths);
    };
  }, [isMounted]);

  // Update paths when window loads
  useEffect(() => {
    // Force update after a short delay to account for layout shifts
    if (isMounted) {
      setTimeout(updatePaths, 500);
    }
  }, [isMounted]);


  const downloadResume = () => {
    const link = document.createElement("a");
    link.href = "/Resume.pdf";
    link.download = "Resume.pdf";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const scrollToContact = () => {
    const contactSection = document.getElementById("contact");
    if (contactSection) {
      contactSection.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="relative w-full min-h-screen flex items-center justify-center bg-black overflow-hidden pt-20">
      {/* Dynamic Background SVG Container */}
      <div ref={containerRef} className="absolute inset-0 pointer-events-none z-10 w-full h-full">
        {isMounted && (
          <svg className="w-full h-full overflow-visible">
            <defs>
              <linearGradient id="lineGradientLeft" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#ec4899" />
                <stop offset="100%" stopColor="#22d3ee" />
              </linearGradient>
              <linearGradient id="lineGradientRight" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#ec4899" />
                <stop offset="100%" stopColor="#22d3ee" />
              </linearGradient>
            </defs>
            <path
              d={svgPaths.left}
              fill="none"
              stroke="url(#lineGradientLeft)"
              strokeWidth="3"
              strokeLinecap="round"
              className="drop-shadow-[0_0_10px_rgba(236,72,153,0.5)] transition-all duration-300 ease-out"
            />
            <path
              d={svgPaths.right}
              fill="none"
              stroke="url(#lineGradientRight)"
              strokeWidth="3"
              strokeLinecap="round"
              className="drop-shadow-[0_0_10px_rgba(34,211,238,0.5)] transition-all duration-300 ease-out"
            />
          </svg>
        )}
      </div>

      <div className="relative z-20 container mx-auto px-4 lg:px-6">
        {/* Profile Picture Section */}
        <div ref={avatarRef} className="relative z-30 flex justify-center mb-8 lg:mb-12">
          <div className="relative w-40 h-40 md:w-56 md:h-56 rounded-full p-1 bg-gradient-to-r from-pink-500 via-purple-500 to-cyan-500 shadow-[0_0_50px_rgba(236,72,153,0.5)]">
            <div className="w-full h-full rounded-full overflow-hidden border-4 border-background bg-background">
              <img
                src={personalInfo.profilePic}
                alt="Profile"
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start w-full transition-all duration-300">

          {/* Left Video */}
          <div className="relative z-30 lg:col-span-3 flex justify-center lg:justify-end order-2 lg:order-1 pt-4">
            <div ref={leftVideoWrapperRef} className="relative group bg-background rounded-xl w-full max-w-[320px] lg:max-w-full aspect-square shadow-[0_0_30px_rgba(236,72,153,0.3)] hover:shadow-[0_0_50px_rgba(236,72,153,0.5)] transition-shadow duration-300">
              <video
                ref={leftVideoRef}
                src="https://res.cloudinary.com/dtzaicj6s/video/upload/f_auto,q_auto/v1766402043/intro_left.mp4"
                autoPlay
                playsInline
                loop
                muted={isLeftMuted}
                className="w-full h-full rounded-xl object-cover border-2 border-pink-500/30"
              />
              <button
                onClick={() => toggleMute(leftVideoRef, setIsLeftMuted)}
                className="absolute bottom-3 right-3 p-2.5 bg-background/60 backdrop-blur-sm rounded-full text-foreground hover:bg-background/90 transition-all duration-200 border border-white/10"
              >
                {isLeftMuted ? <VolumeX size={18} /> : <Volume2 size={18} />}
              </button>
            </div>
          </div>

          {/* Central Text Content */}
          <div className="relative text-center z-30 lg:col-span-6 order-1 lg:order-2 px-2">
            <Badge variant="outline" className="mb-6 py-1.5 px-4 border-white/10 bg-white/5 backdrop-blur-sm"><span className="animate-pulse mr-2 text-green-400 font-bold text-xl">•</span>Available for New Opportunities</Badge>
            <h1 className="text-5xl md:text-7xl font-bold mb-6 tracking-tight bg-clip-text text-transparent bg-gradient-to-b from-white to-gray-400">{personalInfo.name}</h1>
            <div className="text-xl md:text-2xl font-medium mb-8 space-y-2 md:space-y-0 text-gray-300">
              <span className="text-cyan-400 font-semibold">{personalInfo.title.split('|')[0]}</span>
              {personalInfo.title.includes('|') && (<span className="hidden md:inline mx-2 text-gray-600">|</span>)}
              {personalInfo.title.includes('|') && (<span className="text-pink-400 font-semibold block md:inline">{personalInfo.title.split('|')[1]}</span>)}
            </div>
            <p className="text-lg text-muted-foreground mb-10 max-w-2xl mx-auto leading-relaxed">{personalInfo.heroSummary}</p>
            <div className="flex flex-col sm:flex-row gap-5 justify-center items-center">
              <Button
                onClick={downloadResume}
                size="lg"
                className="min-w-[180px] h-12 text-base bg-gradient-to-r from-pink-600 to-purple-600 text-white hover:from-pink-700 hover:to-purple-700 border-0 shadow-lg shadow-pink-900/20"
              >
                <Download className="w-5 h-5 mr-2" />Download Resume
              </Button>
              <Button
                onClick={scrollToContact}
                size="lg"
                className="min-w-[180px] h-12 text-base bg-white/10 text-white hover:bg-white/20 border-white/10 backdrop-blur-sm"
              >
                <Mail className="w-5 h-5 mr-2" />Get in Touch
              </Button>
            </div>
          </div>

          {/* Right Video */}
          <div className="relative z-30 lg:col-span-3 flex justify-center lg:justify-start order-3 lg:order-3 pt-4">
            <div ref={rightVideoWrapperRef} className="relative group bg-background rounded-xl w-full max-w-[320px] lg:max-w-full aspect-square shadow-[0_0_30px_rgba(34,211,238,0.3)] hover:shadow-[0_0_50px_rgba(34,211,238,0.5)] transition-shadow duration-300">
              <video
                ref={rightVideoRef}
                src="https://res.cloudinary.com/dtzaicj6s/video/upload/f_auto,q_auto/v1766401977/intro_right.mp4"
                autoPlay
                playsInline
                loop
                muted={isRightMuted}
                className="w-full h-full rounded-xl object-cover border-2 border-cyan-500/30"
              />
              <button
                onClick={() => toggleMute(rightVideoRef, setIsRightMuted)}
                className="absolute bottom-3 right-3 p-2.5 bg-background/60 backdrop-blur-sm rounded-full text-foreground hover:bg-background/90 transition-all duration-200 border border-white/10"
              >
                {isRightMuted ? <VolumeX size={18} /> : <Volume2 size={18} />}
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default HeroSection;
