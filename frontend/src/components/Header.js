import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Download, Mail, Phone, MapPin, Linkedin, Menu, X } from 'lucide-react';

const Header = ({ personalInfo }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const downloadResume = () => {
    const link = document.createElement('a');
    link.href = '/ALTHAF_HUSSAIN_SYED_DevOps_Resume.pdf';
    link.download = 'ALTHAF_HUSSAIN_SYED_DevOps_Resume.pdf';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    setIsMenuOpen(false);
  };

  return (
    <header className="bg-black/95 backdrop-blur-sm border-b border-cyan-400/20 sticky top-0 z-50 shadow-lg shadow-cyan-400/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Logo/Name */}
          <div className="flex-shrink-0">
            <h1 className="text-2xl font-bold text-white hover:text-cyan-400 transition-colors cursor-pointer neon-glow"
                onClick={() => scrollToSection('hero')}>
              {personalInfo.name}
            </h1>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-8">
            <button 
              onClick={() => scrollToSection('about')}
              className="text-gray-300 hover:text-cyan-400 font-medium transition-colors hover:glow-text"
            >
              About
            </button>
            <button 
              onClick={() => scrollToSection('skills')}
              className="text-gray-300 hover:text-cyan-400 font-medium transition-colors hover:glow-text"
            >
              Skills
            </button>
            <button 
              onClick={() => scrollToSection('experience')}
              className="text-gray-300 hover:text-cyan-400 font-medium transition-colors hover:glow-text"
            >
              Experience
            </button>
            <button 
              onClick={() => scrollToSection('certifications')}
              className="text-gray-300 hover:text-cyan-400 font-medium transition-colors hover:glow-text"
            >
              Certifications
            </button>
            <button 
              onClick={() => scrollToSection('contact')}
              className="text-gray-300 hover:text-cyan-400 font-medium transition-colors hover:glow-text"
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
              className="border-cyan-400 text-cyan-400 bg-black hover:bg-cyan-400 hover:text-black transition-all duration-200 neon-border"
            >
              <Download className="w-4 h-4 mr-2" />
              Resume
            </Button>
            <Button
              onClick={() => scrollToSection('contact')}
              size="sm"
              className="bg-gradient-to-r from-pink-500 to-cyan-400 hover:from-pink-600 hover:to-cyan-500 text-black font-semibold transition-all duration-200 hover:shadow-lg hover:shadow-cyan-400/50 neon-button"
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
              className="text-gray-300 hover:text-cyan-400"
            >
              {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden pb-4 border-t border-cyan-400/20 mt-4">
            <div className="flex flex-col space-y-3 pt-4">
              <button 
                onClick={() => scrollToSection('about')}
                className="text-left text-gray-300 hover:text-cyan-400 font-medium transition-colors py-2"
              >
                About
              </button>
              <button 
                onClick={() => scrollToSection('skills')}
                className="text-left text-gray-300 hover:text-cyan-400 font-medium transition-colors py-2"
              >
                Skills
              </button>
              <button 
                onClick={() => scrollToSection('experience')}
                className="text-left text-gray-300 hover:text-cyan-400 font-medium transition-colors py-2"
              >
                Experience
              </button>
              <button 
                onClick={() => scrollToSection('certifications')}
                className="text-left text-gray-300 hover:text-cyan-400 font-medium transition-colors py-2"
              >
                Certifications
              </button>
              <button 
                onClick={() => scrollToSection('contact')}
                className="text-left text-gray-300 hover:text-cyan-400 font-medium transition-colors py-2"
              >
                Contact
              </button>
              <div className="flex flex-col space-y-2 pt-2">
                <Button
                  onClick={downloadResume}
                  variant="outline"
                  size="sm"
                  className="border-cyan-400 text-cyan-400 bg-black hover:bg-cyan-400 hover:text-black transition-all duration-200"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download Resume
                </Button>
                <Button
                  onClick={() => scrollToSection('contact')}
                  size="sm"
                  className="bg-gradient-to-r from-pink-500 to-cyan-400 hover:from-pink-600 hover:to-cyan-500 text-black font-semibold transition-all duration-200"
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