import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card } from './ui/card'; // This was in your original file, so I've kept it.
import { useTheme } from '../context/ThemeContext'; // ✨ NEW: Import useTheme hook
// ✨ MODIFIED: Added icons for navigation items
import { 
  Download, Mail, Phone, MapPin, Linkedin, Menu, X, Sun, Moon,
  User, Sparkles, Briefcase, Award, BookOpen, ChevronDown, Filter
} from 'lucide-react'; 
import { useNavigate } from 'react-router-dom';

const Header = ({ personalInfo }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showBlogCategories, setShowBlogCategories] = useState(false);
  const { theme, toggleTheme } = useTheme(); // ✨ NEW: Get theme state and toggle function
  const navigate = useNavigate();

  const downloadResume = () => {
    try {
      const link = document.createElement('a');
      link.href = `${process.env.PUBLIC_URL || ''}/AlthafResume.pdf`;
      link.download = 'AlthafResume.pdf';
      link.style.display = 'none';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      console.log('Resume download initiated from header');
    } catch (error) {
      console.error('Download error:', error);
      window.open(`${process.env.PUBLIC_URL || ''}/AlthafResume.pdf`, '_blank');
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
            {/* ========================================================= */}
            {/* SEAMLESS SPLIT BUTTON: Looks like one, acts like two      */}
            {/* ========================================================= */}
            <div className="relative group">
              {/* 1. The Container: Carries the main 'glassmorphic' style so it looks unified */}
              <div className="glassmorphic-nav-btn flex items-center p-0 gap-0 overflow-hidden border border-white/10">
                
                {/* A. Main Link (Left Side) */}
                <button 
                  onClick={() => scrollToSection('blogs')}
                  className="px-4 py-2 font-medium flex items-center h-full hover:bg-white/5 transition-colors focus:outline-none"
                  title="Go to Blogs Section"
                >
                  <BookOpen className="w-4 h-4 mr-2" />
                  Blogs
                </button>

                {/* B. Vertical Separator (Thin Line) */}
                <div className="w-[1px] h-5 bg-white/20 dark:bg-white/10 mx-0"></div>

                {/* C. Toggle Arrow (Right Side) */}
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowBlogCategories(!showBlogCategories);
                  }}
                  className="px-2 py-2 flex items-center justify-center h-full hover:bg-white/10 transition-colors focus:outline-none"
                  title="Toggle Categories"
                >
                  <ChevronDown className={`w-3 h-3 transition-transform duration-300 ${showBlogCategories ? 'rotate-180' : ''}`} />
                </button>
              </div>
              
              {/* ========================================================= */}
              {/* DROPDOWN MENU (Matches Header Style)                      */}
              {/* ========================================================= */}
              {showBlogCategories && (
                <div className="absolute top-full right-0 mt-2 w-64 bg-background/95 backdrop-blur-md border border-cyan-400/30 rounded-xl shadow-2xl shadow-cyan-900/20 py-2 z-50 fade-in-up">
                  <div className="px-4 py-3 border-b border-border/50 bg-secondary/30">
                    <p className="text-sm font-semibold text-foreground flex items-center">
                      <Filter className="w-3 h-3 mr-2 text-cyan-soft" /> 
                      Filter by Topic
                    </p>
                  </div>
                  <div className="max-h-64 overflow-y-auto py-2 custom-scrollbar">
                    {[
                      'Cloud Computing', 
                      'DevOps', 
                      'AI and ML', 
                      'Cybersecurity', 
                      'Software Development'
                    ].map((category) => (
                      <button
                        key={category}
                        onClick={() => {
                          navigate(`/?category=${encodeURIComponent(category)}#blogs`);
                          setShowBlogCategories(false);
                          scrollToSection('blogs');
                        }}
                        className="w-full text-left px-4 py-2.5 text-sm text-muted-foreground hover:text-cyan-soft hover:bg-cyan-400/10 transition-all duration-200 border-l-2 border-transparent hover:border-cyan-400"
                      >
                        {category}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
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
              className="neon-button bg-gradient-to-r from-pink-500 to-green-500 hover:from-pink-600 hover:to-green-600 dark:from-cyan-500 dark:to-purple-600 dark:hover:from-cyan-600 dark:hover:to-purple-700 text-white font-semibold transition-all duration-300"
            >
              <Download className="w-4 h-4 mr-2" />
              Resume
            </Button>
            <Button
              onClick={() => scrollToSection('contact')}
              size="sm"
              id="contact-nav-button"
              className="neon-button bg-gradient-to-r from-pink-500 to-green-500 hover:from-pink-600 hover:to-green-600 dark:from-cyan-500 dark:to-purple-600 dark:hover:from-cyan-600 dark:hover:to-purple-700 text-white font-semibold transition-all duration-300"
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
                  className="neon-button bg-gradient-to-r from-pink-500 to-green-500 hover:from-pink-600 hover:to-green-600 dark:from-cyan-500 dark:to-purple-600 dark:hover:from-cyan-600 dark:hover:to-purple-700 text-white font-semibold transition-all duration-300 fade-in-right stagger-6"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download Resume
                </Button>
                <Button
                  onClick={() => scrollToSection('contact')}
                  size="sm"
                  id="contact-nav-button-mobile"
                  className="neon-button bg-gradient-to-r from-pink-500 to-green-500 hover:from-pink-600 hover:to-green-600 dark:from-cyan-500 dark:to-purple-600 dark:hover:from-cyan-600 dark:hover:to-purple-700 text-white font-semibold transition-all duration-300 fade-in-right stagger-7"
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
