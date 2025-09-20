import React from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Folder, CheckCircle, ArrowRight } from 'lucide-react';

const ProjectsSection = ({ projects }) => {
  return (
    <section id="projects" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Featured Projects
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Real-world implementations showcasing expertise in cloud infrastructure and DevOps automation
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {projects.map((project, index) => (
            <Card 
              key={index} 
              className="p-6 border border-gray-100 hover:border-blue-200 hover:shadow-lg transition-all duration-200 bg-white group"
            >
              {/* Project Header */}
              <div className="flex items-start space-x-4 mb-6">
                <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:bg-blue-100 transition-colors">
                  <Folder className="w-6 h-6 text-blue-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-blue-700 transition-colors">
                    {project.title}
                  </h3>
                </div>
              </div>

              {/* Project Description */}
              <p className="text-gray-600 mb-6 leading-relaxed">
                {project.description}
              </p>

              {/* Technologies */}
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-gray-900 mb-3">
                  Technologies Used
                </h4>
                <div className="flex flex-wrap gap-2">
                  {project.technologies.map((tech, techIndex) => (
                    <Badge 
                      key={techIndex} 
                      variant="outline" 
                      className="border-blue-200 text-blue-700 bg-blue-50 text-xs px-2 py-1 hover:bg-blue-100 transition-colors"
                    >
                      {tech}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Achievements */}
              <div className="space-y-3">
                <h4 className="text-sm font-semibold text-gray-900">
                  Key Outcomes
                </h4>
                {project.achievements.map((achievement, achievementIndex) => (
                  <div key={achievementIndex} className="flex items-start space-x-3">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <p className="text-gray-600 text-sm leading-relaxed">
                      {achievement}
                    </p>
                  </div>
                ))}
              </div>

              {/* Project Link/Action */}
              <div className="mt-6 pt-4 border-t border-gray-100">
                <div className="flex items-center text-blue-600 text-sm font-medium group-hover:text-blue-700 transition-colors cursor-pointer">
                  <span>View Implementation Details</span>
                  <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Projects Summary */}
        <div className="mt-16 bg-gradient-to-r from-blue-50 to-teal-50 rounded-xl p-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Project Impact Summary
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-8">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">60%</div>
                <div className="text-gray-600 font-medium">Faster Deployments</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">40%</div>
                <div className="text-gray-600 font-medium">Reduced Manual Work</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-teal-600 mb-2">99.9%</div>
                <div className="text-gray-600 font-medium">System Reliability</div>
              </div>
            </div>
            <p className="text-gray-600 mt-6 max-w-2xl mx-auto">
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