import React from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Download, Mail, Linkedin, MapPin, Phone } from 'lucide-react';

const HeroSection = ({ personalInfo }) => {
  const downloadResume = () => {
    try {
      // Create a temporary link element
      const link = document.createElement('a');
      link.href = `${process.env.PUBLIC_URL || ''}/ALTHAF_HUSSAIN_SYED_DevOps_Resume.pdf`;
      link.download = 'Althaf_Hussain_Syed_DevOps_Resume.pdf';
      link.style.display = 'none';
      
      // Add to document, trigger click, then remove
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      console.log('Resume download initiated');
    } catch (error) {
      console.error('Download error:', error);
      // Fallback: open in new tab
      window.open(`${process.env.PUBLIC_URL || ''}/ALTHAF_HUSSAIN_SYED_DevOps_Resume.pdf`, '_blank');
    }
  };

  const scrollToContact = () => {
    const element = document.getElementById('contact');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section id="hero" className="bg-black py-20 lg:py-32 relative overflow-hidden">
      {/* Subtle animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-10 w-72 h-72 bg-cyan-400/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-pink-500/5 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-blue-400/3 rounded-full blur-2xl animate-pulse delay-500"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center max-w-4xl mx-auto">
          {/* Professional Badge */}
          <Badge variant="outline" className="mb-6 text-cyan-soft border-cyan-400/30 bg-black/50 px-4 py-2 hover:bg-cyan-400/5 transition-colors backdrop-blur-sm">
            <span className="animate-pulse mr-2 text-green-soft">●</span>
            Available for New Opportunities
          </Badge>

          {/* Main Heading - Reduced glow */}
          <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight hero-title">
            {personalInfo.name}
          </h1>

          {/* Professional Title */}
          <h2 className="text-xl md:text-2xl font-semibold mb-8 attractive-text">
            <span className="text-cyan-soft">{personalInfo.title.split('|')[0]}</span>
            {personalInfo.title.includes('|') && (
              <span className="text-pink-soft"> | {personalInfo.title.split('|')[1]}</span>
            )}
          </h2>

          {/* Summary */}
          <p className="text-lg md:text-xl text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed">
            {personalInfo.summary}
          </p>

          {/* Contact Info Row */}
          <div className="flex flex-wrap justify-center items-center gap-6 mb-12 text-gray-300">
            <div className="flex items-center gap-2 hover:text-cyan-soft transition-colors">
              <MapPin className="w-4 h-4 text-cyan-soft" />
              <span className="text-sm font-medium">{personalInfo.location}</span>
            </div>
            <div className="flex items-center gap-2 hover:text-pink-soft transition-colors">
              <Mail className="w-4 h-4 text-pink-soft" />
              <a href={`mailto:${personalInfo.email}`} className="text-sm font-medium hover:underline">
                {personalInfo.email}
              </a>
            </div>
            <div className="flex items-center gap-2 hover:text-green-soft transition-colors">
              <Phone className="w-4 h-4 text-green-soft" />
              <a href={`tel:${personalInfo.phone}`} className="text-sm font-medium hover:underline">
                {personalInfo.phone}
              </a>
            </div>
            <div className="flex items-center gap-2 hover:text-blue-soft transition-colors">
              <Linkedin className="w-4 h-4 text-blue-soft" />
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
              className="bg-gradient-to-r from-pink-500/80 to-cyan-400/80 hover:from-pink-500 hover:to-cyan-400 text-black px-8 py-3 text-lg font-bold hover:shadow-lg hover:shadow-cyan-400/30 transition-all duration-200 transform hover:-translate-y-0.5"
            >
              <Download className="w-5 h-5 mr-3" />
              Download Resume
            </Button>
            <Button
              onClick={scrollToContact}
              variant="outline"
              size="lg"
              className="border-cyan-400/50 text-cyan-soft bg-black/50 hover:bg-cyan-400/10 hover:text-cyan-400 px-8 py-3 text-lg font-medium hover:shadow-lg hover:shadow-cyan-400/20 transition-all duration-200 transform hover:-translate-y-0.5 backdrop-blur-sm"
            >
              <Mail className="w-5 h-5 mr-3" />
              Get in Touch
            </Button>
          </div>

          {/* Key Stats */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-2xl mx-auto">
            <div className="text-center p-6 bg-black/50 rounded-lg border border-cyan-400/10 hover:border-cyan-400/20 hover:shadow-lg hover:shadow-cyan-400/10 transition-all backdrop-blur-sm neon-card">
              <div className="text-3xl font-bold text-cyan-soft mb-2">3+</div>
              <div className="text-gray-300 font-medium">Years Experience</div>
            </div>
            <div className="text-center p-6 bg-black/50 rounded-lg border border-pink-500/10 hover:border-pink-500/20 hover:shadow-lg hover:shadow-pink-500/10 transition-all backdrop-blur-sm neon-card">
              <div className="text-3xl font-bold text-pink-soft mb-2">14+</div>
              <div className="text-gray-300 font-medium">Certifications</div>
            </div>
            <div className="text-center p-6 bg-black/50 rounded-lg border border-green-400/10 hover:border-green-400/20 hover:shadow-lg hover:shadow-green-400/10 transition-all backdrop-blur-sm neon-card">
              <div className="text-3xl font-bold text-green-soft mb-2">99.9%</div>
              <div className="text-gray-300 font-medium">Uptime Achieved</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;