import React from 'react';
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

  return (
    <section id="about" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            About Me
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Passionate DevOps engineer specializing in cloud infrastructure and automation solutions
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Professional Summary */}
          <div className="space-y-6">
            <h3 className="text-2xl font-semibold text-gray-900 mb-4">
              Professional Summary
            </h3>
            <p className="text-gray-600 leading-relaxed text-lg">
              {personalInfo.summary}
            </p>
            
            <div className="space-y-4">
              <h4 className="text-lg font-semibold text-gray-900">Key Expertise Areas:</h4>
              <div className="grid grid-cols-2 gap-3">
                <Badge variant="outline" className="border-blue-200 text-blue-700 bg-blue-50 px-3 py-2 justify-start hover:bg-blue-100 transition-colors">
                  Cloud Architecture
                </Badge>
                <Badge variant="outline" className="border-blue-200 text-blue-700 bg-blue-50 px-3 py-2 justify-start hover:bg-blue-100 transition-colors">
                  DevOps Automation
                </Badge>
                <Badge variant="outline" className="border-blue-200 text-blue-700 bg-blue-50 px-3 py-2 justify-start hover:bg-blue-100 transition-colors">
                  CI/CD Pipelines
                </Badge>
                <Badge variant="outline" className="border-blue-200 text-blue-700 bg-blue-50 px-3 py-2 justify-start hover:bg-blue-100 transition-colors">
                  Infrastructure as Code
                </Badge>
                <Badge variant="outline" className="border-blue-200 text-blue-700 bg-blue-50 px-3 py-2 justify-start hover:bg-blue-100 transition-colors">
                  Container Orchestration
                </Badge>
                <Badge variant="outline" className="border-blue-200 text-blue-700 bg-blue-50 px-3 py-2 justify-start hover:bg-blue-100 transition-colors">
                  Storage Solutions
                </Badge>
              </div>
            </div>
          </div>

          {/* Key Achievements */}
          <div className="space-y-6">
            <h3 className="text-2xl font-semibold text-gray-900 mb-6">
              Key Achievements
            </h3>
            <div className="space-y-4">
              {achievements.map((achievement, index) => {
                const IconComponent = iconMap[achievement.title] || Award;
                return (
                  <Card 
                    key={index} 
                    className="p-6 border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all duration-200 group"
                  >
                    <div className="flex items-start space-x-4">
                      <div className="flex-shrink-0 w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center group-hover:bg-blue-100 transition-colors">
                        <IconComponent className="w-6 h-6 text-blue-600" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2 group-hover:text-blue-700 transition-colors">
                          {achievement.title}
                        </h4>
                        <p className="text-gray-600 leading-relaxed">
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
        <div className="mt-16 text-center bg-gray-50 rounded-xl p-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            Why I Love DevOps
          </h3>
          <p className="text-gray-600 max-w-3xl mx-auto text-lg leading-relaxed">
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