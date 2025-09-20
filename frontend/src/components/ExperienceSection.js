import React from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Calendar, MapPin, CheckCircle, Building } from 'lucide-react';

const ExperienceSection = ({ experience }) => {
  return (
    <section id="experience" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Professional Experience
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Building robust, scalable infrastructure solutions at leading technology companies
          </p>
        </div>

        <div className="space-y-8">
          {experience.map((job, index) => (
            <Card key={index} className="p-8 border border-gray-100 hover:border-blue-200 hover:shadow-lg transition-all duration-200 bg-white">
              {/* Company Header */}
              <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
                <div className="flex items-center space-x-4 mb-4 md:mb-0">
                  <div className="w-14 h-14 bg-blue-50 rounded-lg flex items-center justify-center">
                    <Building className="w-7 h-7 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">
                      {job.company}
                    </h3>
                    <h4 className="text-lg font-semibold text-blue-600">
                      {job.position}
                    </h4>
                  </div>
                </div>
                
                <div className="flex flex-col md:items-end space-y-2">
                  <div className="flex items-center text-gray-600">
                    <Calendar className="w-4 h-4 mr-2" />
                    <span className="font-medium">{job.duration}</span>
                  </div>
                  <div className="flex items-center text-gray-600">
                    <MapPin className="w-4 h-4 mr-2" />
                    <span>{job.location}</span>
                  </div>
                </div>
              </div>

              {/* Achievements */}
              <div className="mb-6">
                <h5 className="text-lg font-semibold text-gray-900 mb-4">
                  Key Achievements & Responsibilities
                </h5>
                <div className="space-y-3">
                  {job.achievements.map((achievement, achievementIndex) => (
                    <div key={achievementIndex} className="flex items-start space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                      <p className="text-gray-600 leading-relaxed">
                        {achievement}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Technologies Used */}
              <div>
                <h5 className="text-lg font-semibold text-gray-900 mb-4">
                  Technologies & Tools
                </h5>
                <div className="flex flex-wrap gap-2">
                  {job.technologies.map((tech, techIndex) => (
                    <Badge 
                      key={techIndex} 
                      variant="outline" 
                      className="border-blue-200 text-blue-700 bg-blue-50 px-3 py-1 hover:bg-blue-100 transition-colors"
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
        <div className="mt-16 bg-gradient-to-r from-blue-50 to-teal-50 rounded-xl p-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Career Highlights
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-8">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">40%</div>
                <div className="text-gray-600 font-medium">Reduction in Manual Effort</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">30%</div>
                <div className="text-gray-600 font-medium">Faster Incident Response</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-teal-600 mb-2">99.9%</div>
                <div className="text-gray-600 font-medium">Infrastructure Uptime</div>
              </div>
            </div>
            <p className="text-gray-600 mt-6 max-w-2xl mx-auto">
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