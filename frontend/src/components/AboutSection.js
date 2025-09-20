import React, { useEffect, useRef, useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Award, TrendingUp, Shield, Zap } from 'lucide-react';

const AboutSection = ({ personalInfo, achievements }) => {
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

  return (
    <section id="about" className="py-20 bg-gradient-to-b from-black to-gray-900 relative overflow-hidden">
      {/* Subtle background effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-10 right-20 w-64 h-64 bg-cyan-400/3 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 left-20 w-80 h-80 bg-pink-500/3 rounded-full blur-3xl"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4 section-heading">
            About Me
          </h2>
          <p className="text-lg text-gray-300 max-w-3xl mx-auto">
            Passionate DevOps engineer specializing in cloud infrastructure and automation solutions
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Professional Summary */}
          <div className="space-y-6">
            <h3 className="text-2xl font-semibold mb-4 attractive-text">
              <span className="text-cyan-soft">Professional</span> <span className="text-pink-soft">Summary</span>
            </h3>
            <p className="text-gray-300 leading-relaxed text-lg">
              {personalInfo.summary}
            </p>
            
            <div className="space-y-4">
              <h4 className="text-lg font-semibold text-white">Key Expertise Areas:</h4>
              <div className="grid grid-cols-2 gap-3">
                <Badge variant="outline" className="border-cyan-400/30 text-cyan-soft bg-black/50 px-3 py-2 justify-start hover:bg-cyan-400/5 transition-all backdrop-blur-sm">
                  Cloud Architecture
                </Badge>
                <Badge variant="outline" className="border-pink-500/30 text-pink-soft bg-black/50 px-3 py-2 justify-start hover:bg-pink-500/5 transition-all backdrop-blur-sm">
                  DevOps Automation
                </Badge>
                <Badge variant="outline" className="border-green-400/30 text-green-soft bg-black/50 px-3 py-2 justify-start hover:bg-green-400/5 transition-all backdrop-blur-sm">
                  CI/CD Pipelines
                </Badge>
                <Badge variant="outline" className="border-yellow-400/30 text-yellow-soft bg-black/50 px-3 py-2 justify-start hover:bg-yellow-400/5 transition-all backdrop-blur-sm">
                  Infrastructure as Code
                </Badge>
                <Badge variant="outline" className="border-blue-400/30 text-blue-soft bg-black/50 px-3 py-2 justify-start hover:bg-blue-400/5 transition-all backdrop-blur-sm">
                  Container Orchestration
                </Badge>
                <Badge variant="outline" className="border-purple-400/30 text-purple-soft bg-black/50 px-3 py-2 justify-start hover:bg-purple-400/5 transition-all backdrop-blur-sm">
                  Storage Solutions
                </Badge>
              </div>
            </div>
          </div>

          {/* Key Achievements */}
          <div className="space-y-6">
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
                    className="p-6 bg-black/50 border border-gray-700/30 hover:border-cyan-400/20 hover:shadow-lg hover:shadow-cyan-400/10 transition-all duration-200 group backdrop-blur-sm neon-card"
                  >
                    <div className="flex items-start space-x-4">
                      <div className={`flex-shrink-0 w-12 h-12 bg-gray-900/50 rounded-lg flex items-center justify-center group-hover:bg-gray-800/50 transition-colors border border-gray-700/20`}>
                        <IconComponent className={`w-6 h-6 ${iconColor}`} />
                      </div>
                      <div>
                        <h4 className="font-semibold text-white mb-2 group-hover:text-cyan-soft transition-colors">
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
        <div className="mt-16 text-center bg-black/30 rounded-xl p-8 border border-gray-700/20 backdrop-blur-sm">
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