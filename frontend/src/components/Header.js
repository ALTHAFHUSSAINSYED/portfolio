import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card } from './ui/card'; // This was in your original file, so I've kept it.
import { useTheme } from '../context/ThemeContext'; // ✨ NEW: Import useTheme hook
// ✨ MODIFIED: Added icons for navigation items
import { 
  Download, Mail, Phone, MapPin, Linkedin, Menu, X, Sun, Moon,
  User, Sparkles, Briefcase, Award, BookOpen
} from 'lucide-react'; 

const Header = ({ personalInfo }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { theme, toggleTheme } = useTheme(); // ✨ NEW: Get theme state and toggle function

  const downloadResume = () => {
    try {
      const link = document.createElement('a');
      link.href = `${process.env.PUBLIC_URL || ''}/ALTHAF_HUSSAIN_SYED_DevOps_Resume.pdf`;
      link.download = 'Althaf_Hussain_Syed_DevOps_Resume.pdf';
      link.style.display = 'none';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      console.log('Resume download initiated from header');
    } catch (error) {
      console.error('Download error:', error);
      window.open(`${process.env.PUBLIC_URL || ''}/ALTHAF_HUSSAIN_SYED_DevOps_Resume.pdf`, '_blank');
    }
  };

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      // For Contact section, the dedicated smooth-scroll.js handles this
      // This avoids duplicate event handling for the contact button
      if (sectionId !== 'contact') {
        // Get header height for proper scroll positioning
        const headerHeight = document.querySelector('header').offsetHeight;
        const targetPosition = element.getBoundingClientRect().top + window.pageYOffset - headerHeight;
      
        // Use enhanced smooth scrolling with better positioning
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
      }
    }
    setIsMenuOpen(false);
  };

  return (
    // ✨ MODIFIED: Uses bg-background for theme compatibility
    <header className="bg-background/95 backdrop-blur-sm border-b border-cyan-400/20 sticky top-0 z-50 shadow-lg shadow-cyan-400/5 fade-in">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-3">
          {/* Logo/Name */}
          <div className="flex-shrink-0 mr-6"> {/* Added mr-6 to reduce spacing to About button */}
            <h1
              className={`text-2xl font-bold transition-all duration-300 cursor-pointer hover-scale ${theme === 'dark' ? 'site-title-gradient' : 'name-text-light'}`}
              onClick={() => scrollToSection('hero')}
            >
              {personalInfo.name}
            </h1>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-4"> {/* Reduced space between nav buttons */}
            <button 
              onClick={() => scrollToSection('about')}
              className="glassmorphic-nav-btn font-medium nav-blink-gradient"
            >
              <User className="w-4 h-4 mr-2" />
              About
            </button>
            <button 
              onClick={() => scrollToSection('skills')}
              className="glassmorphic-nav-btn font-medium nav-blink-gradient"
            >
              <Sparkles className="w-4 h-4 mr-2" />
              Skills
            </button>
            <button 
              onClick={() => scrollToSection('experience')}
              className="glassmorphic-nav-btn font-medium nav-blink-gradient"
            >
              <Briefcase className="w-4 h-4 mr-2" />
              Experience
            </button>
            <button 
              onClick={() => scrollToSection('certifications')}
              className="glassmorphic-nav-btn font-medium nav-blink-gradient"
            >
              <Award className="w-4 h-4 mr-2" />
              Certifications
            </button>
            <button 
              onClick={() => scrollToSection('blogs')}
              className="glassmorphic-nav-btn font-medium nav-blink-gradient"
            >
              <BookOpen className="w-4 h-4 mr-2" />
              Blogs
            </button>
          </nav>

          <div className="hidden md:flex items-center space-x-3">
            {/* Theme Toggle left of Resume */}
            <Button
              onClick={toggleTheme}
              variant="ghost"
              size="icon"
              className="theme-toggle-btn theme-toggle-animate mr-2 theme-toggle-glassmorphic"
            >
              {theme === 'dark' ? <Sun className="w-15 h-15 animate-pulse" /> : <Moon className="w-15 h-15 animate-pulse" />}
              <span className="sr-only">Toggle theme</span>
            </Button>
            <Button
              onClick={downloadResume}
              size="sm"
              className="neon-button bg-gradient-to-r from-pink-500/80 to-cyan-400/80 hover:from-pink-500 hover:to-cyan-400 text-black font-semibold transition-all duration-300"
            >
              <Download className="w-4 h-4 mr-2" />
              Resume
            </Button>
            <Button
              onClick={() => scrollToSection('contact')}
              size="sm"
              id="contact-nav-button"
              className="neon-button bg-gradient-to-r from-pink-500/80 to-cyan-400/80 hover:from-pink-500 hover:to-cyan-400 text-black font-semibold transition-all duration-300"
            >
              <Mail className="w-4 h-4 mr-2" />
              Contact
            </Button>
          </div>

          {/* ✨ MODIFIED: Container for mobile buttons */}
          <div className="md:hidden flex items-center gap-2">
            {/* ✨ NEW: Theme Toggle for Mobile */}
            <Button
              onClick={toggleTheme}
              variant="ghost"
              size="icon"
              className="theme-toggle-btn text-foreground hover:text-cyan-soft hover-scale"
            >
              {theme === 'dark' ? <Sun className="w-8 h-8 animate-pulse" /> : <Moon className="w-8 h-8 animate-pulse" />}
            </Button>
             {/* Mobile Menu Button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-foreground hover:text-cyan-soft transition-all duration-300 hover-rotate"
            >
              {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Menu with Slide Animation */}
        <div className={`md:hidden transition-all duration-300 ease-in-out overflow-hidden ${
          isMenuOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
        }`}>
          <div className="pb-4 border-t border-cyan-400/20 mt-4">
            <div className="flex flex-col space-y-3 pt-4">
              {[
                {section: 'about', icon: <User className="w-4 h-4 mr-2" />},
                {section: 'skills', icon: <Sparkles className="w-4 h-4 mr-2" />},
                {section: 'experience', icon: <Briefcase className="w-4 h-4 mr-2" />},
                {section: 'certifications', icon: <Award className="w-4 h-4 mr-2" />},
                {section: 'blogs', icon: <BookOpen className="w-4 h-4 mr-2" />}
              ].map(({section, icon}, index) => (
                <button 
                  key={section}
                  onClick={() => scrollToSection(section)}
                  className={`text-left text-foreground hover:text-cyan-soft font-medium transition-all duration-300 py-2 capitalize fade-in-right stagger-${index + 1} flex items-center`}
                >
                  {icon}
                  {section.charAt(0).toUpperCase() + section.slice(1)}
                </button>
              ))}
              <div className="flex flex-col space-y-2 pt-2">
                <Button
                  onClick={downloadResume}
                  size="sm"
                  className="neon-button bg-gradient-to-r from-pink-500/80 to-cyan-400/80 hover:from-pink-500 hover:to-cyan-400 text-black font-semibold transition-all duration-300 fade-in-right stagger-6"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download Resume
                </Button>
                <Button
                  onClick={() => scrollToSection('contact')}
                  size="sm"
                  id="contact-nav-button-mobile"
                  className="neon-button bg-gradient-to-r from-pink-500/80 to-cyan-400/80 hover:from-pink-500 hover:to-cyan-400 text-black font-semibold transition-all duration-300 fade-in-right stagger-7"
                >
                  <Mail className="w-4 h-4 mr-2" />
                  Contact
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
