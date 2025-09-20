import React, { useEffect, useRef, useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Folder, CheckCircle, ArrowRight, Zap, Code, Server } from 'lucide-react';

const ProjectsSection = ({ projects }) => {
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

    return () => observer.disconnect();
  }, []);

  const getProjectIcon = (title) => {
    if (title.toLowerCase().includes('pipeline')) return Code;
    if (title.toLowerCase().includes('infrastructure')) return Server;
    if (title.toLowerCase().includes('storage')) return Folder;
    return Zap;
  };

  const getProjectColor = (index) => {
    const colors = ['text-cyan-soft', 'text-pink-soft', 'text-green-soft'];
    return colors[index % colors.length];
  };

  const getProjectBg = (index) => {
    const backgrounds = ['bg-cyan-400/10', 'bg-pink-500/10', 'bg-green-400/10'];
    return backgrounds[index % backgrounds.length];
  };

  const getProjectBorder = (index) => {
    const borders = ['border-cyan-400/30', 'border-pink-500/30', 'border-green-400/30'];
    return borders[index % borders.length];
  };

  return (
    <section id="projects" className="py-20 bg-black relative overflow-hidden" ref={sectionRef}>
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
        
        {/* Project-themed floating elements */}
        <div className="absolute top-1/5 right-1/4 w-8 h-8 bg-cyan-400/10 rounded-lg floating opacity-30 rotate-45"></div>
        <div className="absolute bottom-1/3 left-1/5 w-6 h-6 bg-pink-500/10 rounded-lg floating-reverse opacity-25 rotate-12"></div>
        <div className="absolute top-2/3 right-1/3 w-10 h-10 bg-green-400/10 rounded-lg bounce-glow opacity-20 -rotate-12"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16">
          <h2 className={`text-3xl md:text-4xl font-bold mb-4 shine-text ${isVisible ? 'fade-in-up' : ''}`}>
            Featured Projects
          </h2>
          <p className={`text-lg text-gray-300 max-w-3xl mx-auto glow-text ${isVisible ? 'fade-in-up stagger-1' : ''}`}>
            Real-world implementations showcasing expertise in cloud infrastructure and DevOps automation
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {projects.map((project, index) => {
            const IconComponent = getProjectIcon(project.title);
            const projectColor = getProjectColor(index);
            const projectBg = getProjectBg(index);
            const projectBorder = getProjectBorder(index);
            
            return (
              <Card 
                key={index} 
                className={`p-6 bg-black/80 border border-gray-700/30 hover:border-cyan-400/40 transition-all duration-500 backdrop-blur-sm neon-card hover-lift hover-shine group ${
                  isVisible ? `scale-in stagger-${index + 2}` : ''
                }`}
              >
                {/* Project Header */}
                <div className="flex items-start space-x-4 mb-6">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 ${projectBg} border ${projectBorder} group-hover:scale-110 transition-all duration-300 hover-rotate`}>
                    <IconComponent className={`w-6 h-6 ${projectColor} pulse-shine`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-cyan-soft transition-all duration-300 shine-text-slow">
                      {project.title}
                    </h3>
                  </div>
                </div>

                {/* Project Description */}
                <p className="text-gray-300 mb-6 leading-relaxed glow-text">
                  {project.description}
                </p>

                {/* Technologies */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-white mb-3 sparkle-text">
                    Technologies Used
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {project.technologies.map((tech, techIndex) => (
                      <Badge 
                        key={techIndex} 
                        variant="outline" 
                        className={`border-cyan-400/30 text-cyan-soft bg-black/50 text-xs px-2 py-1 hover:bg-cyan-400/10 transition-all duration-300 hover-scale sparkle-text ${
                          isVisible ? `fade-in-up stagger-${techIndex + 4}` : ''
                        }`}
                      >
                        {tech}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Achievements */}
                <div className="space-y-3 mb-6">
                  <h4 className="text-sm font-semibold text-white sparkle-text">
                    Key Outcomes
                  </h4>
                  {project.achievements.map((achievement, achievementIndex) => (
                    <div 
                      key={achievementIndex} 
                      className={`flex items-start space-x-3 hover-glow transition-all duration-300 p-2 rounded ${
                        isVisible ? `fade-in-right stagger-${achievementIndex + 5}` : ''
                      }`}
                    >
                      <CheckCircle className="w-4 h-4 text-green-soft mt-0.5 flex-shrink-0 pulse-shine" />
                      <p className="text-gray-300 text-sm leading-relaxed glow-text">
                        {achievement}
                      </p>
                    </div>
                  ))}
                </div>

                {/* Project Link/Action */}
                <div className="pt-4 border-t border-gray-700/30">
                  <div className="flex items-center text-cyan-soft text-sm font-medium group-hover:text-cyan-400 transition-all duration-300 cursor-pointer hover-glow p-2 rounded sparkle-text">
                    <span>View Implementation Details</span>
                    <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-2 transition-transform duration-300" />
                  </div>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Projects Summary */}
        <div className={`mt-16 bg-black/60 rounded-xl p-8 border border-gray-700/30 backdrop-blur-sm neon-card hover-lift ${
          isVisible ? 'slide-in-bottom stagger-8' : ''
        }`}>
          <div className="text-center">
            <h3 className="text-2xl font-bold mb-4 shine-text">
              Project Impact Summary
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-8">
              <div className="text-center hover-glow transition-all duration-300 p-6 rounded-lg bg-cyan-400/5 border border-cyan-400/20">
                <div className="text-3xl font-bold text-cyan-soft mb-2 counter glow-text-strong">60%</div>
                <div className="text-gray-300 font-medium glow-text">Faster Deployments</div>
              </div>
              <div className="text-center hover-glow transition-all duration-300 p-6 rounded-lg bg-green-400/5 border border-green-400/20">
                <div className="text-3xl font-bold text-green-soft mb-2 counter glow-text-strong">40%</div>
                <div className="text-gray-300 font-medium glow-text">Reduced Manual Work</div>
              </div>
              <div className="text-center hover-glow transition-all duration-300 p-6 rounded-lg bg-pink-500/5 border border-pink-500/20">
                <div className="text-3xl font-bold text-pink-soft mb-2 counter glow-text-strong">99.9%</div>
                <div className="text-gray-300 font-medium glow-text">System Reliability</div>
              </div>
            </div>
            <p className="text-gray-300 mt-6 max-w-2xl mx-auto glow-text">
              Each project demonstrates practical application of DevOps principles to solve real business challenges 
              while improving efficiency and reliability.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ProjectsSection;