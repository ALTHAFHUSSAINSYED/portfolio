import React, { useState } from 'react';
import { Button } from './ui/button';
import { useTheme } from '../context/ThemeContext'; // ✨ NEW: Import useTheme hook
import { Download, Mail, Menu, X, Sun, Moon } from 'lucide-react'; // ✨ NEW: Import Sun and Moon icons

const Header = ({ personalInfo }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { theme, toggleTheme } = useTheme(); // ✨ NEW: Get theme state and toggle function

  const downloadResume = () => {
    // ... (your existing download function)
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
    // ... (your existing scroll function)
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    setIsMenuOpen(false);
  };

  return (
    <header className="bg-background/95 backdrop-blur-sm border-b border-cyan-400/20 sticky top-0 z-50 shadow-lg shadow-cyan-400/5 fade-in">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Logo/Name */}
          <div className="flex-shrink-0">
            <h1 className="text-2xl font-bold text-foreground hover:text-cyan-soft transition-all duration-300 cursor-pointer hover-scale"
                onClick={() => scrollToSection('hero')}>
              {personalInfo.name}
            </h1>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-8">
            {/* ... (your existing navigation buttons) ... */}
            <button onClick={() => scrollToSection('about')} className="nav-link font-medium transition-all duration-300">About</button>
            <button onClick={() => scrollToSection('skills')} className="nav-link font-medium transition-all duration-300">Skills</button>
            <button onClick={() => scrollToSection('experience')} className="nav-link font-medium transition-all duration-300">Experience</button>
            <button onClick={() => scrollToSection('certifications')} className="nav-link font-medium transition-all duration-300">Certifications</button>
            <button onClick={() => scrollToSection('contact')} className="nav-link font-medium transition-all duration-300">Contact</button>
          </nav>

          {/* Action Buttons */}
          <div className="hidden md:flex items-center space-x-3">
            <Button
              onClick={downloadResume}
              variant="outline"
              size="sm"
              className="border-cyan-400/50 text-cyan-soft bg-transparent hover:bg-cyan-400/10 hover:text-cyan-400 transition-all duration-300 hover-glow"
            >
              <Download className="w-4 h-4 mr-2" />
              Resume
            </Button>
            <Button
              onClick={() => scrollToSection('contact')}
              size="sm"
              className="neon-button bg-gradient-to-r from-pink-500/80 to-cyan-400/80 hover:from-pink-500 hover:to-cyan-400 text-black font-semibold transition-all duration-300"
            >
              <Mail className="w-4 h-4 mr-2" />
              Contact
            </Button>
            {/* ✨ NEW: Theme Toggle Button */}
            <Button
              onClick={toggleTheme}
              variant="ghost"
              size="icon"
              className="text-foreground hover:text-cyan-soft transition-all duration-300 hover-rotate"
            >
              {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              <span className="sr-only">Toggle theme</span>
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center gap-2">
            {/* ✨ NEW: Theme Toggle for Mobile */}
            <Button
              onClick={toggleTheme}
              variant="ghost"
              size="sm"
              className="text-foreground hover:text-cyan-soft"
            >
              {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-foreground hover:text-cyan-soft transition-all duration-300"
            >
              {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Menu */}
        {/* ... (your existing mobile menu logic) ... */}
      </div>
    </header>
  );
};

export default Header;
