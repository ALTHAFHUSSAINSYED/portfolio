import React, { useEffect, useRef, useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Calendar, MapPin, CheckCircle, Building } from 'lucide-react';

const ExperienceSection = ({ experience }) => {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => {
        if (sectionRef.current) {
            observer.unobserve(sectionRef.current);
        }
    };
  }, []);

  return (
    // ✨ MODIFIED: Changed bg-black to bg-background
    <section id="experience" className="py-20 bg-background relative overflow-hidden" ref={sectionRef}>
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="absolute top-1/3 right-1/4 w-1 h-1 bg-cyan-400 rounded-full floating opacity-40"></div>
        <div className="absolute bottom-1/4 left-1/4 w-2 h-2 bg-pink-500 rounded-full bounce-glow opacity-30"></div>
        <div className="absolute top-3/4 right-1/3 w-1.5 h-1.5 bg-green-400 rounded-full floating-reverse opacity-35"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16">
          <h2 className={`text-3xl md:text-4xl font-bold mb-4 shine-text ${isVisible ? 'fade-in-up' : ''}`}>
            Professional Experience
          </h2>
          {/* ✨ MODIFIED: Changed text-gray-300 to text-muted-foreground */}
          <p className={`text-lg text-muted-foreground max-w-3xl mx-auto glow-text ${isVisible ? 'fade-in-up stagger-1' : ''}`}>
            Building robust, scalable infrastructure solutions at leading technology companies
          </p>
        </div>

        <div className="space-y-8">
          {experience.map((job, index) => (
            // ✨ MODIFIED: Removed redundant/conflicting color classes to let neon-card work
            <Card 
              key={index} 
              className={`p-8 transition-all duration-500 backdrop-blur-sm neon-card hover-lift hover-shine ${
                isVisible ? `fade-in-up stagger-${index + 2}` : ''
              }`}
            >
              {/* Company Header */}
              <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
                <div className="flex items-center space-x-4 mb-4 md:mb-0">
                  <div className="w-14 h-14 bg-gradient-to-r from-cyan-400/20 to-pink-500/20 rounded-lg flex items-center justify-center hover-rotate transition-all duration-300 border border-cyan-400/30">
                    <Building className="w-7 h-7 text-cyan-soft glow-text" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold shine-text-slow">
                      {job.company}
                    </h3>
                    <h4 className="text-lg font-semibold text-gradient-animate">
                      {job.position}
                    </h4>
                  </div>
                </div>
                
                <div className="flex flex-col md:items-end space-y-2">
                  {/* ✨ MODIFIED: Changed text-gray-300 to text-muted-foreground */}
                  <div className="flex items-center text-muted-foreground glow-text">
                    <Calendar className="w-4 h-4 mr-2 text-cyan-soft" />
                    <span className="font-medium">{job.duration}</span>
                  </div>
                   {/* ✨ MODIFIED: Changed text-gray-300 to text-muted-foreground */}
                  <div className="flex items-center text-muted-foreground glow-text">
                    <MapPin className="w-4 h-4 mr-2 text-pink-soft" />
                    <span>{job.location}</span>
                  </div>
                </div>
              </div>

              {/* Achievements */}
              <div className="mb-6">
                <h5 className="text-lg font-semibold mb-4 shine-text">
                  Key Achievements & Responsibilities
                </h5>
                <div className="space-y-3">
                  {job.achievements.map((achievement, achievementIndex) => (
                    <div 
                      key={achievementIndex} 
                      className={`flex items-start space-x-3 hover-glow transition-all duration-300 p-2 rounded ${
                        isVisible ? `fade-in-right stagger-${achievementIndex + 3}` : ''
                      }`}
                    >
                      <CheckCircle className="w-5 h-5 text-green-soft mt-0.5 flex-shrink-0 pulse-shine" />
                      {/* ✨ MODIFIED: Changed text-gray-300 to text-muted-foreground */}
                      <p className="text-muted-foreground leading-relaxed glow-text">
                        {achievement}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Technologies Used */}
              <div>
                <h5 className="text-lg font-semibold mb-4 shine-text">
                  Technologies & Tools
                </h5>
                <div className="flex flex-wrap gap-3">
                  {job.technologies.map((tech, techIndex) => (
                    <Badge 
                      key={techIndex} 
                      variant="outline" 
                      // ✨ MODIFIED: Changed bg-black/50 to bg-background/50
                      className={`border-cyan-400/30 text-cyan-soft bg-background/50 px-3 py-1 hover:bg-cyan-400/10 transition-all duration-300 hover-scale hover-glow sparkle-text ${
                        isVisible ? `scale-in stagger-${techIndex + 1}` : ''
                      }`}
                    >
                      {tech}
                    </Badge>
                  ))}
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Experience Summary */}
        {/* ✨ MODIFIED: Removed redundant/conflicting color classes to let neon-card work */}
        <div className={`mt-16 rounded-xl p-8 backdrop-blur-sm neon-card hover-lift ${
          isVisible ? 'slide-in-bottom stagger-6' : ''
        }`}>
          <div className="text-center">
            <h3 className="text-2xl font-bold mb-4 shine-text">
              Career Highlights
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-8">
              <div className="text-center hover-glow transition-all duration-300 p-4 rounded-lg">
                <div className="text-3xl font-bold text-cyan-soft mb-2 counter glow-text-strong">40%</div>
                {/* ✨ MODIFIED: Changed text-gray-300 to text-muted-foreground */}
                <div className="text-muted-foreground font-medium glow-text">Reduction in Manual Effort</div>
              </div>
              <div className="text-center hover-glow transition-all duration-300 p-4 rounded-lg">
                <div className="text-3xl font-bold text-green-soft mb-2 counter glow-text-strong">30%</div>
                {/* ✨ MODIFIED: Changed text-gray-300 to text-muted-foreground */}
                <div className="text-muted-foreground font-medium glow-text">Faster Incident Response</div>
              </div>
              <div className="text-center hover-glow transition-all duration-300 p-4 rounded-lg">
                <div className="text-3xl font-bold text-pink-soft mb-2 counter glow-text-strong">99.9%</div>
                {/* ✨ MODIFIED: Changed text-gray-300 to text-muted-foreground */}
                <div className="text-muted-foreground font-medium glow-text">Infrastructure Uptime</div>
              </div>
            </div>
            {/* ✨ MODIFIED: Changed text-gray-300 to text-muted-foreground */}
            <p className="text-muted-foreground mt-6 max-w-2xl mx-auto glow-text">
              Consistently delivering measurable business impact through innovative DevOps practices 
              and cloud infrastructure solutions.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ExperienceSection;
