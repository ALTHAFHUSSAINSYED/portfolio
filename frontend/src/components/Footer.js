import React from 'react';
import { Button } from './ui/button';
import { Linkedin, Mail, Phone, Download, ArrowUp } from 'lucide-react';

const Footer = ({ personalInfo }) => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const downloadResume = () => {
    try {
      const link = document.createElement('a');
      link.href = `${process.env.PUBLIC_URL || ''}/ALTHAF_HUSSAIN_SYED_DevOps_Resume.pdf`;
      link.download = 'Althaf_Hussain_Syed_DevOps_Resume.pdf';
      link.style.display = 'none';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      console.log('Resume download initiated from footer');
    } catch (error) {
      console.error('Download error:', error);
      window.open(`${process.env.PUBLIC_URL || ''}/ALTHAF_HUSSAIN_SYED_DevOps_Resume.pdf`, '_blank');
    }
  };

  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* Personal Info */}
          <div className="space-y-4">
            <h3 className="text-2xl font-bold text-white mb-4">
              {personalInfo.name}
            </h3>
            <p className="text-gray-300 text-lg">
              {personalInfo.title}
            </p>
            <p className="text-gray-400 leading-relaxed">
              Building scalable cloud infrastructure and DevOps solutions that drive business success.
            </p>
          </div>

          {/* Quick Links */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-white mb-4">
              Quick Links
            </h4>
            <div className="space-y-2">
              <button 
                onClick={() => document.getElementById('about')?.scrollIntoView({ behavior: 'smooth' })}
                className="block text-gray-300 hover:text-blue-400 transition-colors text-left"
              >
                About Me
              </button>
              <button 
                onClick={() => document.getElementById('skills')?.scrollIntoView({ behavior: 'smooth' })}
                className="block text-gray-300 hover:text-blue-400 transition-colors text-left"
              >
                Technical Skills
              </button>
              <button 
                onClick={() => document.getElementById('experience')?.scrollIntoView({ behavior: 'smooth' })}
                className="block text-gray-300 hover:text-blue-400 transition-colors text-left"
              >
                Experience
              </button>
              <button 
                onClick={() => document.getElementById('certifications')?.scrollIntoView({ behavior: 'smooth' })}
                className="block text-gray-300 hover:text-blue-400 transition-colors text-left"
              >
                Certifications
              </button>
              <button 
                onClick={() => document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' })}
                className="block text-gray-300 hover:text-blue-400 transition-colors text-left"
              >
                Contact
              </button>
            </div>
          </div>

          {/* Contact & Actions */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-white mb-4">
              Get in Touch
            </h4>
            
            {/* Contact Info */}
            <div className="space-y-3">
              <a 
                href={`mailto:${personalInfo.email}`}
                className="flex items-center space-x-3 text-gray-300 hover:text-blue-400 transition-colors"
              >
                <Mail className="w-4 h-4" />
                <span>{personalInfo.email}</span>
              </a>
              <a 
                href={`tel:${personalInfo.phone}`}
                className="flex items-center space-x-3 text-gray-300 hover:text-blue-400 transition-colors"
              >
                <Phone className="w-4 h-4" />
                <span>{personalInfo.phone}</span>
              </a>
              <a 
                href={personalInfo.linkedin}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-3 text-gray-300 hover:text-blue-400 transition-colors"
              >
                <Linkedin className="w-4 h-4" />
                <span>LinkedIn Profile</span>
              </a>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3 pt-4">
              <Button
                onClick={downloadResume}
                size="sm"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 hover:shadow-lg"
              >
                <Download className="w-4 h-4 mr-2" />
                Download Resume
              </Button>
              <Button
                onClick={() => window.open(personalInfo.linkedin, '_blank')}
                variant="outline"
                size="sm"
                className="w-full border-gray-600 text-gray-300 hover:bg-gray-800 hover:border-gray-500 transition-all duration-200"
              >
                <Linkedin className="w-4 h-4 mr-2" />
                Connect on LinkedIn
              </Button>
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-gray-800 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            {/* Copyright */}
            <div className="text-center md:text-left">
              <p className="text-gray-400">
                © {currentYear} {personalInfo.name}. All rights reserved.
              </p>
              <p className="text-gray-500 text-sm mt-1">
                Built with React & Tailwind CSS
              </p>
            </div>

            {/* Availability Status */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-gray-300 text-sm font-medium">
                  Available for new opportunities
                </span>
              </div>
              
              {/* Back to Top */}
              <Button
                onClick={scrollToTop}
                variant="outline"
                size="sm"
                className="border-gray-600 text-gray-300 hover:bg-gray-800 hover:border-gray-500 transition-all duration-200"
              >
                <ArrowUp className="w-4 h-4 mr-2" />
                Back to Top
              </Button>
            </div>
          </div>
        </div>

        {/* Professional Statement */}
        <div className="mt-8 text-center">
          <p className="text-gray-400 text-sm max-w-2xl mx-auto">
            Dedicated to delivering exceptional DevOps solutions that empower teams to build, 
            deploy, and scale applications with confidence and reliability.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;