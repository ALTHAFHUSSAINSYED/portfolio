import React, { useEffect, useRef, useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Award, TrendingUp, Shield, Zap } from 'lucide-react';

const AboutSection = ({ personalInfo, achievements }) => {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);

  const iconMap = {
    'Infrastructure Automation Champion': TrendingUp,
    'Multi-Cloud Expert': Shield,
    'Incident Response Optimization': Zap,
    'High Availability Specialist': Award
  };

  const iconColors = {
    'Infrastructure Automation Champion': 'text-cyan-soft',
    'Multi-Cloud Expert': 'text-pink-soft',
    'Incident Response Optimization': 'text-green-soft',
    'High Availability Specialist': 'text-yellow-soft'
  };

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

  return (
    <section id="about" className="py-20 bg-gradient-to-b from-black to-gray-900 relative overflow-hidden" ref={sectionRef}>
      {/* Animated background effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="absolute top-1/4 right-1/4 w-1 h-1 bg-cyan-400 rounded-full floating opacity-30"></div>
        <div className="absolute bottom-1/3 left-1/3 w-2 h-2 bg-pink-500 rounded-full bounce-slow opacity-20"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16">
          <h2 className={`text-3xl md:text-4xl font-bold mb-4 text-gradient-animate ${isVisible ? 'fade-in-up' : ''}`}>
            About Me
          </h2>
          <p className={`text-lg text-gray-300 max-w-3xl mx-auto ${isVisible ? 'fade-in-up stagger-1' : ''}`}>
            Passionate DevOps engineer specializing in cloud infrastructure and automation solutions
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Professional Summary */}
          <div className={`space-y-6 ${isVisible ? 'fade-in-left stagger-2' : ''}`}>
            <h3 className="text-2xl font-semibold mb-4 attractive-text">
              <span className="text-cyan-soft">Professional</span> <span className="text-pink-soft">Summary</span>
            </h3>
            <p className="text-gray-300 leading-relaxed text-lg">
              {personalInfo.summary}
            </p>
            
            <div className="space-y-4">
              <h4 className="text-lg font-semibold text-white">Key Expertise Areas:</h4>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { name: 'Cloud Architecture', color: 'cyan' },
                  { name: 'DevOps Automation', color: 'pink' },
                  { name: 'CI/CD Pipelines', color: 'green' },
                  { name: 'Infrastructure as Code', color: 'yellow' },
                  { name: 'Container Orchestration', color: 'blue' },
                  { name: 'Storage Solutions', color: 'purple' }
                ].map((skill, index) => (
                  <Badge 
                    key={skill.name}
                    variant="outline" 
                    className={`border-${skill.color}-400/30 text-${skill.color}-soft bg-black/50 px-3 py-2 justify-start hover:bg-${skill.color}-400/5 transition-all duration-300 backdrop-blur-sm hover-scale ${
                      isVisible ? `fade-in-up stagger-${index + 3}` : ''
                    }`}
                  >
                    {skill.name}
                  </Badge>
                ))}
              </div>
            </div>
          </div>

          {/* Key Achievements */}
          <div className={`space-y-6 ${isVisible ? 'fade-in-right stagger-3' : ''}`}>
            <h3 className="text-2xl font-semibold mb-6 attractive-text">
              <span className="text-pink-soft">Key</span> <span className="text-cyan-soft">Achievements</span>
            </h3>
            <div className="space-y-4">
              {achievements.map((achievement, index) => {
                const IconComponent = iconMap[achievement.title] || Award;
                const iconColor = iconColors[achievement.title] || 'text-cyan-soft';
                return (
                  <Card 
                    key={index} 
                    className={`p-6 bg-black/50 border border-gray-700/30 hover:border-cyan-400/20 transition-all duration-300 group backdrop-blur-sm neon-card hover-lift ${
                      isVisible ? `fade-in-up stagger-${index + 4}` : ''
                    }`}
                  >
                    <div className="flex items-start space-x-4">
                      <div className={`flex-shrink-0 w-12 h-12 bg-gray-900/50 rounded-lg flex items-center justify-center group-hover:bg-gray-800/50 transition-all duration-300 border border-gray-700/20 hover-rotate`}>
                        <IconComponent className={`w-6 h-6 ${iconColor}`} />
                      </div>
                      <div>
                        <h4 className="font-semibold text-white mb-2 group-hover:text-cyan-soft transition-colors duration-300">
                          {achievement.title}
                        </h4>
                        <p className="text-gray-300 leading-relaxed">
                          {achievement.description}
                        </p>
                      </div>
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        </div>

        {/* Personal Touch */}
        <div className={`mt-16 text-center bg-black/30 rounded-xl p-8 border border-gray-700/20 backdrop-blur-sm neon-card hover-lift transition-all duration-300 ${
          isVisible ? 'slide-in-bottom stagger-6' : ''
        }`}>
          <h3 className="text-xl font-semibold text-white mb-4">
            <span className="text-green-soft">Why I Love</span> <span className="text-blue-soft">DevOps</span>
          </h3>
          <p className="text-gray-300 max-w-3xl mx-auto text-lg leading-relaxed">
            I'm passionate about bridging the gap between development and operations, creating robust, 
            scalable systems that enable teams to deliver value faster and more reliably. Every 
            automation script, every pipeline optimization, and every infrastructure improvement 
            is an opportunity to make technology work better for people.
          </p>
        </div>
      </div>
    </section>
  );
};

export default AboutSection;