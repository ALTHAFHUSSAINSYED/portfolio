import React from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Download, Mail, Linkedin, MapPin, Phone } from 'lucide-react';

const HeroSection = ({ personalInfo }) => {
  const downloadResume = () => {
    const link = document.createElement('a');
    link.href = '/ALTHAF_HUSSAIN_SYED_DevOps_Resume.pdf';
    link.download = 'ALTHAF_HUSSAIN_SYED_DevOps_Resume.pdf';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const scrollToContact = () => {
    const element = document.getElementById('contact');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section id="hero" className="bg-black py-20 lg:py-32 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-10 w-72 h-72 bg-cyan-400/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-green-400/5 rounded-full blur-2xl animate-pulse delay-500"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center max-w-4xl mx-auto">
          {/* Professional Badge */}
          <Badge variant="outline" className="mb-6 text-cyan-400 border-cyan-400 bg-black/50 px-4 py-2 hover:bg-cyan-400/10 transition-colors neon-border backdrop-blur-sm">
            <span className="animate-pulse mr-2">●</span>
            Available for New Opportunities
          </Badge>

          {/* Main Heading */}
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6 leading-tight neon-glow">
            {personalInfo.name}
          </h1>

          {/* Professional Title */}
          <h2 className="text-xl md:text-2xl text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-pink-500 font-semibold mb-8">
            {personalInfo.title}
          </h2>

          {/* Summary */}
          <p className="text-lg md:text-xl text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed">
            {personalInfo.summary}
          </p>

          {/* Contact Info Row */}
          <div className="flex flex-wrap justify-center items-center gap-6 mb-12 text-gray-300">
            <div className="flex items-center gap-2 hover:text-cyan-400 transition-colors">
              <MapPin className="w-4 h-4 text-cyan-400" />
              <span className="text-sm font-medium">{personalInfo.location}</span>
            </div>
            <div className="flex items-center gap-2 hover:text-cyan-400 transition-colors">
              <Mail className="w-4 h-4 text-pink-500" />
              <a href={`mailto:${personalInfo.email}`} className="text-sm font-medium hover:underline">
                {personalInfo.email}
              </a>
            </div>
            <div className="flex items-center gap-2 hover:text-cyan-400 transition-colors">
              <Phone className="w-4 h-4 text-green-400" />
              <a href={`tel:${personalInfo.phone}`} className="text-sm font-medium hover:underline">
                {personalInfo.phone}
              </a>
            </div>
            <div className="flex items-center gap-2 hover:text-cyan-400 transition-colors">
              <Linkedin className="w-4 h-4 text-blue-400" />
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
              className="bg-gradient-to-r from-pink-500 to-cyan-400 hover:from-pink-600 hover:to-cyan-500 text-black px-8 py-3 text-lg font-bold hover:shadow-lg hover:shadow-cyan-400/50 transition-all duration-200 transform hover:-translate-y-0.5 neon-button"
            >
              <Download className="w-5 h-5 mr-3" />
              Download Resume
            </Button>
            <Button
              onClick={scrollToContact}
              variant="outline"
              size="lg"
              className="border-cyan-400 text-cyan-400 bg-black/50 hover:bg-cyan-400 hover:text-black px-8 py-3 text-lg font-medium hover:shadow-lg hover:shadow-cyan-400/50 transition-all duration-200 transform hover:-translate-y-0.5 neon-border backdrop-blur-sm"
            >
              <Mail className="w-5 h-5 mr-3" />
              Get in Touch
            </Button>
          </div>

          {/* Key Stats */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-2xl mx-auto">
            <div className="text-center p-6 bg-black/50 rounded-lg border border-cyan-400/20 hover:border-cyan-400/50 hover:shadow-lg hover:shadow-cyan-400/20 transition-all backdrop-blur-sm neon-card">
              <div className="text-3xl font-bold text-cyan-400 mb-2 neon-text">3+</div>
              <div className="text-gray-300 font-medium">Years Experience</div>
            </div>
            <div className="text-center p-6 bg-black/50 rounded-lg border border-pink-500/20 hover:border-pink-500/50 hover:shadow-lg hover:shadow-pink-500/20 transition-all backdrop-blur-sm neon-card">
              <div className="text-3xl font-bold text-pink-500 mb-2 neon-text">14+</div>
              <div className="text-gray-300 font-medium">Certifications</div>
            </div>
            <div className="text-center p-6 bg-black/50 rounded-lg border border-green-400/20 hover:border-green-400/50 hover:shadow-lg hover:shadow-green-400/20 transition-all backdrop-blur-sm neon-card">
              <div className="text-3xl font-bold text-green-400 mb-2 neon-text">99.9%</div>
              <div className="text-gray-300 font-medium">Uptime Achieved</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;