import React from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Download, Mail, Linkedin, MapPin, Phone } from 'lucide-react';

const HeroSection = ({ personalInfo }) => {
  const downloadResume = () => {
    // In a real implementation, this would download the actual resume
    alert('Resume download feature - to be implemented with actual resume file');
  };

  const scrollToContact = () => {
    const element = document.getElementById('contact');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section id="hero" className="bg-gradient-to-br from-gray-50 to-blue-50 py-20 lg:py-32">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-4xl mx-auto">
          {/* Professional Badge */}
          <Badge variant="outline" className="mb-6 text-blue-700 border-blue-200 bg-blue-50 px-4 py-2 hover:bg-blue-100 transition-colors">
            Available for New Opportunities
          </Badge>

          {/* Main Heading */}
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            {personalInfo.name}
          </h1>

          {/* Professional Title */}
          <h2 className="text-xl md:text-2xl text-blue-600 font-semibold mb-8">
            {personalInfo.title}
          </h2>

          {/* Summary */}
          <p className="text-lg md:text-xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed">
            {personalInfo.summary}
          </p>

          {/* Contact Info Row */}
          <div className="flex flex-wrap justify-center items-center gap-6 mb-12 text-gray-600">
            <div className="flex items-center gap-2 hover:text-blue-600 transition-colors">
              <MapPin className="w-4 h-4" />
              <span className="text-sm font-medium">{personalInfo.location}</span>
            </div>
            <div className="flex items-center gap-2 hover:text-blue-600 transition-colors">
              <Mail className="w-4 h-4" />
              <a href={`mailto:${personalInfo.email}`} className="text-sm font-medium hover:underline">
                {personalInfo.email}
              </a>
            </div>
            <div className="flex items-center gap-2 hover:text-blue-600 transition-colors">
              <Phone className="w-4 h-4" />
              <a href={`tel:${personalInfo.phone}`} className="text-sm font-medium hover:underline">
                {personalInfo.phone}
              </a>
            </div>
            <div className="flex items-center gap-2 hover:text-blue-600 transition-colors">
              <Linkedin className="w-4 h-4" />
              <a 
                href={personalInfo.linkedin} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-sm font-medium hover:underline"
              >
                LinkedIn Profile
              </a>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              onClick={downloadResume}
              size="lg"
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 text-lg font-medium hover:shadow-lg transition-all duration-200 transform hover:-translate-y-0.5"
            >
              <Download className="w-5 h-5 mr-3" />
              Download Resume
            </Button>
            <Button
              onClick={scrollToContact}
              variant="outline"
              size="lg"
              className="border-blue-200 text-blue-700 hover:bg-blue-50 hover:border-blue-300 px-8 py-3 text-lg font-medium hover:shadow-lg transition-all duration-200 transform hover:-translate-y-0.5"
            >
              <Mail className="w-5 h-5 mr-3" />
              Get in Touch
            </Button>
          </div>

          {/* Key Stats */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-2xl mx-auto">
            <div className="text-center p-6 bg-white rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="text-3xl font-bold text-blue-600 mb-2">3+</div>
              <div className="text-gray-600 font-medium">Years Experience</div>
            </div>
            <div className="text-center p-6 bg-white rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="text-3xl font-bold text-blue-600 mb-2">14+</div>
              <div className="text-gray-600 font-medium">Certifications</div>
            </div>
            <div className="text-center p-6 bg-white rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="text-3xl font-bold text-blue-600 mb-2">99.9%</div>
              <div className="text-gray-600 font-medium">Uptime Achieved</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;