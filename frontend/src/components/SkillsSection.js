import React, { useEffect, useRef, useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Cloud, Settings, Code, Database, Award } from 'lucide-react';

const SkillsSection = ({ skills }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [progressValues, setProgressValues] = useState({});
  const sectionRef = useRef(null);

  const skillCategories = [
    {
      title: 'Cloud Platforms',
      icon: Cloud,
      items: skills.cloudPlatforms,
      color: 'bg-blue-50 border-blue-200 text-blue-700',
      gradient: 'from-cyan-400 to-blue-500'
    },
    {
      title: 'DevOps Tools',
      icon: Settings,
      items: skills.devopsTools,
      color: 'bg-green-50 border-green-200 text-green-700',
      gradient: 'from-green-400 to-emerald-500'
    },
    {
      title: 'Programming',
      icon: Code,
      items: skills.programming,
      color: 'bg-purple-50 border-purple-200 text-purple-700',
      gradient: 'from-purple-400 to-pink-500'
    },
    {
      title: 'Storage & Infrastructure',
      icon: Database,
      items: skills.storage,
      color: 'bg-orange-50 border-orange-200 text-orange-700',
      gradient: 'from-orange-400 to-red-500'
    }
  ];

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          // Animate progress bars
          setTimeout(() => {
            const newProgressValues = {};
            skillCategories.forEach(category => {
              category.items.forEach(skill => {
                newProgressValues[skill.name] = getSkillLevel(skill.level);
              });
            });
            setProgressValues(newProgressValues);
          }, 500);
        }
      },
      { threshold: 0.1 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  const getSkillLevel = (level) => {
    const levels = {
      'Expert': 95,
      'Advanced': 85,
      'Intermediate': 70,
      'Beginner': 50
    };
    return levels[level] || 50;
  };

  const getLevelColor = (level) => {
    const colors = {
      'Expert': 'text-green-soft',
      'Advanced': 'text-cyan-soft',
      'Intermediate': 'text-yellow-soft',
      'Beginner': 'text-gray-400'
    };
    return colors[level] || 'text-gray-400';
  };

  const getProgressColor = (level) => {
    const colors = {
      'Expert': 'bg-green-soft',
      'Advanced': 'bg-cyan-soft',
      'Intermediate': 'bg-yellow-soft',
      'Beginner': 'bg-gray-400'
    };
    return colors[level] || 'bg-gray-400';
  };

  return (
    <section id="skills" className="py-20 bg-gradient-to-b from-gray-900 to-black relative overflow-hidden" ref={sectionRef}>
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16">
          <h2 className={`text-3xl md:text-4xl font-bold mb-4 text-gradient-animate ${isVisible ? 'fade-in-up' : ''}`}>
            Technical Skills
          </h2>
          <p className={`text-lg text-gray-300 max-w-3xl mx-auto ${isVisible ? 'fade-in-up stagger-1' : ''}`}>
            Comprehensive expertise across cloud platforms, DevOps tools, and modern infrastructure technologies
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {skillCategories.map((category, categoryIndex) => {
            const IconComponent = category.icon;
            return (
              <Card 
                key={categoryIndex} 
                className={`p-6 bg-black/50 border border-gray-700/30 hover:border-cyan-400/30 transition-all duration-500 backdrop-blur-sm neon-card hover-lift ${
                  isVisible ? `fade-in-up stagger-${categoryIndex + 2}` : ''
                }`}
              >
                <div className="flex items-center mb-6">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center mr-4 bg-gradient-to-r ${category.gradient} hover-rotate transition-all duration-300`}>
                    <IconComponent className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-white">
                    {category.title}
                  </h3>
                </div>

                <div className="space-y-6">
                  {category.items.map((skill, skillIndex) => (
                    <div 
                      key={skillIndex} 
                      className={`space-y-3 ${isVisible ? `fade-in-right stagger-${skillIndex + 1}` : ''}`}
                    >
                      <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-3">
                          <span className="font-medium text-white hover:text-cyan-soft transition-colors duration-300">
                            {skill.name}
                          </span>
                          {skill.certifications && (
                            <Badge 
                              variant="outline" 
                              className="border-yellow-400/30 text-yellow-soft bg-yellow-400/5 text-xs px-2 py-1 hover-scale transition-all duration-300"
                            >
                              <Award className="w-3 h-3 mr-1" />
                              {skill.certifications} certs
                            </Badge>
                          )}
                        </div>
                        <span className={`text-sm font-medium ${getLevelColor(skill.level)}`}>
                          {skill.level}
                        </span>
                      </div>
                      <div className="relative">
                        <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                          <div 
                            className={`h-full ${getProgressColor(skill.level)} progress-fill transition-all duration-2000 ease-out`}
                            style={{ 
                              width: `${progressValues[skill.name] || 0}%`,
                              transition: 'width 2s ease-out'
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            );
          })}
        </div>

        {/* Skills Summary with Animation */}
        <div className={`mt-16 text-center ${isVisible ? 'slide-in-bottom stagger-6' : ''}`}>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-2xl mx-auto">
            <div className="bg-black/50 rounded-lg p-6 border border-cyan-400/20 hover:border-cyan-400/40 transition-all duration-300 neon-card hover-lift">
              <div className="text-2xl font-bold text-cyan-soft mb-2 counter">4</div>
              <div className="text-gray-300 font-medium text-sm">Cloud Platforms</div>
            </div>
            <div className="bg-black/50 rounded-lg p-6 border border-green-400/20 hover:border-green-400/40 transition-all duration-300 neon-card hover-lift">
              <div className="text-2xl font-bold text-green-soft mb-2 counter">6+</div>
              <div className="text-gray-300 font-medium text-sm">DevOps Tools</div>
            </div>
            <div className="bg-black/50 rounded-lg p-6 border border-purple-400/20 hover:border-purple-400/40 transition-all duration-300 neon-card hover-lift">
              <div className="text-2xl font-bold text-purple-soft mb-2 counter">3</div>
              <div className="text-gray-300 font-medium text-sm">Languages</div>
            </div>
            <div className="bg-black/50 rounded-lg p-6 border border-orange-400/20 hover:border-orange-400/40 transition-all duration-300 neon-card hover-lift">
              <div className="text-2xl font-bold text-yellow-soft mb-2 counter">4+</div>
              <div className="text-gray-300 font-medium text-sm">Storage Systems</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SkillsSection;