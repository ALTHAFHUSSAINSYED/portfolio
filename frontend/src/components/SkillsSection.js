import React from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Cloud, Settings, Code, Database, Award } from 'lucide-react';

const SkillsSection = ({ skills }) => {
  const skillCategories = [
    {
      title: 'Cloud Platforms',
      icon: Cloud,
      items: skills.cloudPlatforms,
      color: 'bg-blue-50 border-blue-200 text-blue-700'
    },
    {
      title: 'DevOps Tools',
      icon: Settings,
      items: skills.devopsTools,
      color: 'bg-green-50 border-green-200 text-green-700'
    },
    {
      title: 'Programming',
      icon: Code,
      items: skills.programming,
      color: 'bg-purple-50 border-purple-200 text-purple-700'
    },
    {
      title: 'Storage & Infrastructure',
      icon: Database,
      items: skills.storage,
      color: 'bg-orange-50 border-orange-200 text-orange-700'
    }
  ];

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
      'Expert': 'text-green-600',
      'Advanced': 'text-blue-600',
      'Intermediate': 'text-yellow-600',
      'Beginner': 'text-gray-600'
    };
    return colors[level] || 'text-gray-600';
  };

  return (
    <section id="skills" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Technical Skills
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Comprehensive expertise across cloud platforms, DevOps tools, and modern infrastructure technologies
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {skillCategories.map((category, categoryIndex) => {
            const IconComponent = category.icon;
            return (
              <Card key={categoryIndex} className="p-6 border border-gray-100 hover:border-blue-200 hover:shadow-lg transition-all duration-200 bg-white">
                <div className="flex items-center mb-6">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center mr-4 ${category.color}`}>
                    <IconComponent className="w-6 h-6" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900">
                    {category.title}
                  </h3>
                </div>

                <div className="space-y-4">
                  {category.items.map((skill, skillIndex) => (
                    <div key={skillIndex} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-3">
                          <span className="font-medium text-gray-900">
                            {skill.name}
                          </span>
                          {skill.certifications && (
                            <Badge variant="outline" className="border-yellow-200 text-yellow-700 bg-yellow-50 text-xs px-2 py-1">
                              <Award className="w-3 h-3 mr-1" />
                              {skill.certifications} certs
                            </Badge>
                          )}
                        </div>
                        <span className={`text-sm font-medium ${getLevelColor(skill.level)}`}>
                          {skill.level}
                        </span>
                      </div>
                      <Progress 
                        value={getSkillLevel(skill.level)} 
                        className="h-2 bg-gray-200"
                      />
                    </div>
                  ))}
                </div>
              </Card>
            );
          })}
        </div>

        {/* Skills Summary */}
        <div className="mt-16 text-center">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-2xl mx-auto">
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="text-2xl font-bold text-blue-600 mb-2">4</div>
              <div className="text-gray-600 font-medium text-sm">Cloud Platforms</div>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="text-2xl font-bold text-green-600 mb-2">6+</div>
              <div className="text-gray-600 font-medium text-sm">DevOps Tools</div>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="text-2xl font-bold text-purple-600 mb-2">3</div>
              <div className="text-gray-600 font-medium text-sm">Languages</div>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="text-2xl font-bold text-orange-600 mb-2">4+</div>
              <div className="text-gray-600 font-medium text-sm">Storage Systems</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SkillsSection;