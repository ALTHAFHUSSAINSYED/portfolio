import React, { useRef, useEffect, useState } from "react";
import { Volume2, VolumeX } from "lucide-react";

const HeroSection = () => {
  const video1Ref = useRef(null);
  const video2Ref = useRef(null);
  const [isMuted1, setIsMuted1] = useState(true);
  const [isMuted2, setIsMuted2] = useState(true);

  // Auto mute on scroll
  useEffect(() => {
    const handleScroll = () => {
      if (video1Ref.current) video1Ref.current.muted = true;
      if (video2Ref.current) video2Ref.current.muted = true;
      setIsMuted1(true);
      setIsMuted2(true);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <section className="relative flex justify-center items-start gap-32 mt-20">
      {/* Left Video (Automation, CI/CD side) */}
      <div className="relative w-[720px] h-[480px] shadow-2xl rounded-2xl overflow-hidden">
        <video
          ref={video1Ref}
          src="/video1.mp4"
          autoPlay
          loop
          muted
          playsInline
          preload="metadata"
          className="w-full h-full object-cover"
        />
        <button
          onClick={() => {
            video1Ref.current.muted = !video1Ref.current.muted;
            setIsMuted1(video1Ref.current.muted);
          }}
          className="absolute top-3 right-3 bg-black bg-opacity-70 p-3 rounded-full"
        >
          {isMuted1 ? (
            <VolumeX size={28} color="white" />
          ) : (
            <Volume2 size={28} color="white" />
          )}
        </button>
      </div>

      {/* Center Profile */}
      <div className="relative z-20 flex flex-col items-center text-center">
        <img
          src="/profile.png"
          alt="Profile"
          className="w-56 h-56 rounded-full border-4 border-cyan-400 shadow-xl"
        />
        <h1 className="mt-4 text-3xl font-bold text-white">Althaf Hussain Syed</h1>
        <h2 className="text-xl text-cyan-400">
          DevOps Engineer | Cloud & Infrastructure Specialist
        </h2>
        <p className="text-gray-300 mt-2 max-w-md">
          Certified DevOps Engineer with 3+ years of experience in cloud infrastructure,
          automation, and CI/CD pipeline engineering. Multi-cloud certified professional
          with expertise in AWS, GCP, Azure, and Oracle Cloud.
        </p>
      </div>

      {/* Right Video (Professional with… side) */}
      <div className="relative w-[720px] h-[480px] shadow-2xl rounded-2xl overflow-hidden">
        <video
          ref={video2Ref}
          src="/video2.mp4"
          autoPlay
          loop
          muted
          playsInline
          preload="metadata"
          className="w-full h-full object-cover"
        />
        <button
          onClick={() => {
            video2Ref.current.muted = !video2Ref.current.muted;
            setIsMuted2(video2Ref.current.muted);
          }}
          className="absolute top-3 right-3 bg-black bg-opacity-70 p-3 rounded-full"
        >
          {isMuted2 ? (
            <VolumeX size={28} color="white" />
          ) : (
            <Volume2 size={28} color="white" />
          )}
        </button>
      </div>

      {/* Snake crawling from profile to left video */}
      <img
        src="/snake.png"
        alt="snake-left"
        className="absolute w-48 h-20 animate-snake-left"
      />

      {/* Snake crawling from profile to right video */}
      <img
        src="/snake.png"
        alt="snake-right"
        className="absolute w-48 h-20 animate-snake-right"
      />

      <style jsx>{`
        /* Snake path left */
        @keyframes snakePathLeft {
          0% {
            offset-distance: 0%;
          }
          50% {
            offset-distance: 100%;
          }
          100% {
            offset-distance: 0%;
          }
        }

        /* Snake path right */
        @keyframes snakePathRight {
          0% {
            offset-distance: 0%;
          }
          50% {
            offset-distance: 100%;
          }
          100% {
            offset-distance: 0%;
          }
        }

        .animate-snake-left {
          top: 150px;
          left: 200px;
          offset-path: path("M 600 300 C 450 350, 300 400, 100 500");
          offset-rotate: auto;
          animation: snakePathLeft 12s ease-in-out infinite;
        }

        .animate-snake-right {
          top: 150px;
          right: 200px;
          offset-path: path("M 600 300 C 750 350, 900 400, 1100 500");
          offset-rotate: auto;
          animation: snakePathRight 12s ease-in-out infinite;
        }
      `}</style>
    </section>
  );
};

export default HeroSection;
