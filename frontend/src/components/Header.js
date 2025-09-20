import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Download, Mail, Phone, MapPin, Linkedin, Menu, X } from 'lucide-react';

const Header = ({ personalInfo }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const downloadResume = () => {
    // In a real implementation, this would download the actual resume
    alert('Resume download feature - to be implemented with actual resume file');
  };

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    setIsMenuOpen(false);
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-100 sticky top-0 z-50 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Logo/Name */}
          <div className="flex-shrink-0">
            <h1 className="text-2xl font-bold text-gray-900 hover:text-blue-600 transition-colors cursor-pointer"
                onClick={() => scrollToSection('hero')}>
              {personalInfo.name}
            </h1>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-8">
            <button 
              onClick={() => scrollToSection('about')}
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
            >
              About
            </button>
            <button 
              onClick={() => scrollToSection('skills')}
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
            >
              Skills
            </button>
            <button 
              onClick={() => scrollToSection('experience')}
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
            >
              Experience
            </button>
            <button 
              onClick={() => scrollToSection('certifications')}
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
            >
              Certifications
            </button>
            <button 
              onClick={() => scrollToSection('contact')}
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
            >
              Contact
            </button>
          </nav>

          {/* Action Buttons */}
          <div className="hidden md:flex items-center space-x-3">
            <Button
              onClick={downloadResume}
              variant="outline"
              size="sm"
              className="border-blue-200 text-blue-700 hover:bg-blue-50 hover:border-blue-300 transition-all duration-200"
            >
              <Download className="w-4 h-4 mr-2" />
              Resume
            </Button>
            <Button
              onClick={() => scrollToSection('contact')}
              size="sm"
              className="bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 hover:shadow-md"
            >
              <Mail className="w-4 h-4 mr-2" />
              Contact
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-700"
            >
              {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden pb-4 border-t border-gray-100 mt-4">
            <div className="flex flex-col space-y-3 pt-4">
              <button 
                onClick={() => scrollToSection('about')}
                className="text-left text-gray-700 hover:text-blue-600 font-medium transition-colors py-2"
              >
                About
              </button>
              <button 
                onClick={() => scrollToSection('skills')}
                className="text-left text-gray-700 hover:text-blue-600 font-medium transition-colors py-2"
              >
                Skills
              </button>
              <button 
                onClick={() => scrollToSection('experience')}
                className="text-left text-gray-700 hover:text-blue-600 font-medium transition-colors py-2"
              >
                Experience
              </button>
              <button 
                onClick={() => scrollToSection('certifications')}
                className="text-left text-gray-700 hover:text-blue-600 font-medium transition-colors py-2"
              >
                Certifications
              </button>
              <button 
                onClick={() => scrollToSection('contact')}
                className="text-left text-gray-700 hover:text-blue-600 font-medium transition-colors py-2"
              >
                Contact
              </button>
              <div className="flex flex-col space-y-2 pt-2">
                <Button
                  onClick={downloadResume}
                  variant="outline"
                  size="sm"
                  className="border-blue-200 text-blue-700 hover:bg-blue-50 hover:border-blue-300 transition-all duration-200"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download Resume
                </Button>
                <Button
                  onClick={() => scrollToSection('contact')}
                  size="sm"
                  className="bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200"
                >
                  <Mail className="w-4 h-4 mr-2" />
                  Get in Touch
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;