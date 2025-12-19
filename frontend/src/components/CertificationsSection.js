import React, { useEffect, useRef, useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Award, Calendar, Filter } from 'lucide-react';

const CertificationsSection = ({ certifications }) => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => {
        if (sectionRef.current) {
            observer.unobserve(sectionRef.current);
        }
    };
  }, []);

  const categories = {
    all: { name: 'All Certifications', color: 'text-gray-900 dark:text-white', bg: 'bg-gray-200 dark:bg-gray-600/20' },
    aws: { name: 'AWS', color: 'text-orange-600 dark:text-orange-400', bg: 'bg-orange-100 dark:bg-orange-500/20' },
    gcp: { name: 'Google Cloud', color: 'text-blue-600 dark:text-blue-400', bg: 'bg-blue-100 dark:bg-blue-500/20' },
    azure: { name: 'Microsoft Azure', color: 'text-blue-700 dark:text-blue-500', bg: 'bg-blue-100 dark:bg-blue-600/20' },
    oracle: { name: 'Oracle', color: 'text-red-600 dark:text-red-400', bg: 'bg-red-100 dark:bg-red-500/20' },
    devops: { name: 'DevOps', color: 'text-green-600 dark:text-green-400', bg: 'bg-green-100 dark:bg-green-500/20' },
    ai: { name: 'AI/ML', color: 'text-purple-600 dark:text-purple-400', bg: 'bg-purple-100 dark:bg-purple-500/20' },
    github: { name: 'GitHub', color: 'text-gray-700 dark:text-gray-300', bg: 'bg-gray-200 dark:bg-gray-500/20' }
  };

  const filteredCertifications = selectedCategory === 'all' 
    ? certifications 
    : certifications.filter(cert => 
        Array.isArray(cert.category) 
          ? cert.category.includes(selectedCategory)
          : cert.category === selectedCategory
      );

  const getMainCategory = (category) => {
    return Array.isArray(category) ? category[0] : category;
  };

  const getCertificationIcon = (category) => {
    return <Award className="w-6 h-6" />;
  };

  const getCertificationColor = (category) => {
    return categories[getMainCategory(category)]?.color || 'text-gray-400';
  };

  const getCertificationBg = (category) => {
    return categories[getMainCategory(category)]?.bg || 'bg-gray-500/20';
  };

  return (
    // ✨ MODIFIED: Changed bg-black to bg-background
    <section id="certifications" className="py-20 bg-background relative overflow-hidden" ref={sectionRef}>
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
        
        {/* Floating certification icons */}
        <div className="absolute top-1/4 left-1/5 w-6 h-6 bg-orange-400/20 rounded-full floating opacity-20"></div>
        <div className="absolute top-2/3 right-1/5 w-4 h-4 bg-blue-400/20 rounded-full floating-reverse opacity-25"></div>
        <div className="absolute bottom-1/4 left-1/3 w-5 h-5 bg-green-400/20 rounded-full bounce-glow opacity-30"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16">
          <h2 className={`text-3xl md:text-4xl font-bold mb-4 shine-text ${isVisible ? 'fade-in-up' : ''}`}>
            Certifications & Credentials
          </h2>
          {/* ✨ MODIFIED: Changed text-gray-300 to text-muted-foreground */}
          <p className={`text-lg text-muted-foreground max-w-3xl mx-auto glow-text ${isVisible ? 'fade-in-up stagger-1' : ''}`}>
            Industry-recognized certifications across multiple cloud platforms and technologies
          </p>
        </div>

        {/* Filter Buttons */}
        <div className={`flex flex-wrap justify-center gap-3 mb-12 ${isVisible ? 'fade-in-up stagger-2' : ''}`}>
          {Object.entries(categories).map(([key, category], index) => (
            <Button
              key={key}
              onClick={() => setSelectedCategory(key)}
              variant={selectedCategory === key ? 'default' : 'outline'}
              size="sm"
              // ✨ MODIFIED: Unselected state is now theme-aware
              className={`transition-all duration-300 hover-shine sparkle-text ${
                selectedCategory === key 
                  ? 'neon-button bg-gradient-to-r from-cyan-500/80 to-pink-500/80 text-black font-bold' 
                  : 'border-border/50 text-muted-foreground bg-background/50 hover:bg-secondary/50 hover-glow'
              } ${isVisible ? `scale-in stagger-${index + 3}` : ''}`}
            >
              <Filter className="w-4 h-4 mr-2" />
              {category.name}
            </Button>
          ))}
        </div>

        {/* Certifications Count */}
        <div className={`text-center mb-8 ${isVisible ? 'fade-in-up stagger-3' : ''}`}>
          <Badge 
            variant="outline" 
            // ✨ MODIFIED: Changed bg-black/50 to bg-background/50
            className="border-cyan-400/50 text-cyan-soft bg-background/50 px-6 py-3 text-lg sparkle-text hover-glow transition-all duration-300"
          >
            <Award className="w-5 h-5 mr-2 pulse-shine" />
            {filteredCertifications.length} {selectedCategory === 'all' ? 'Total' : categories[selectedCategory]?.name} Certifications
          </Badge>
        </div>

        {/* Certifications Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCertifications.map((cert, index) => (
            // ✨ MODIFIED: Removed redundant/conflicting color classes to let neon-card work
            <Card 
              key={index} 
              className={`p-6 transition-all duration-500 backdrop-blur-sm neon-card hover-lift hover-shine group ${
                isVisible ? `rotate-in stagger-${index + 4}` : ''
              }`}
            >
              <div className="flex items-start space-x-4">
                {/* ✨ MODIFIED: Changed border to be theme-aware */}
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 ${getCertificationBg(cert.category)} group-hover:scale-110 transition-all duration-300 hover-rotate border border-border/30`}>
                  <div className={`${getCertificationColor(cert.category)} glow-text`}>
                    {getCertificationIcon(cert.category)}
                  </div>
                </div>
                
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 dark:text-foreground mb-2 leading-tight group-hover:text-cyan-600 dark:group-hover:text-cyan-400 transition-all duration-300 shine-text-slow">
                    {cert.name}
                  </h3>
                  {/* ✨ MODIFIED: Changed text-gray-300 to text-muted-foreground */}
                  <p className="text-muted-foreground text-sm mb-3 font-medium glow-text">
                    {cert.issuer}
                  </p>
                  {/* ✨ MODIFIED: Changed text-gray-400 to text-muted-foreground */}
                  <div className="flex items-center text-muted-foreground text-sm">
                    <Calendar className="w-4 h-4 mr-2 text-green-soft pulse-shine" />
                    <span className="glow-text">{cert.year}</span>
                  </div>
                </div>
              </div>
              
              {/* ✨ MODIFIED: Changed border to be theme-aware */}
              <div className="mt-4 pt-4 border-t border-border/30">
                <Badge 
                  variant="outline" 
                  className={`${getCertificationBg(cert.category)} ${getCertificationColor(cert.category)} border-current text-xs px-3 py-1 hover-scale transition-all duration-300 sparkle-text`}
                >
                  {selectedCategory !== 'all' && Array.isArray(cert.category) && cert.category.includes(selectedCategory)
                    ? categories[selectedCategory]?.name
                    : categories[getMainCategory(cert.category)]?.name || cert.category}
                </Badge>
              </div>
            </Card>
          ))}
        </div>

        {/* Certification Summary Stats */}
        {/* ✨ MODIFIED: Removed redundant/conflicting color classes to let neon-card work */}
        <div className={`mt-16 rounded-xl p-8 shadow-sm backdrop-blur-sm neon-card hover-lift ${
          isVisible ? 'slide-in-bottom stagger-8' : ''
        }`}>
          <h3 className="text-2xl font-bold text-center mb-8 shine-text">
            Certification Portfolio Overview
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center p-4 bg-orange-500/10 rounded-lg border border-orange-400/20 hover:border-orange-400/40 transition-all duration-300 hover-glow">
              <div className="text-2xl font-bold text-orange-400 mb-2 counter glow-text-strong">
                {certifications.filter(c => Array.isArray(c.category) ? c.category.includes('aws') : c.category === 'aws').length}
              </div>
              {/* ✨ MODIFIED: Changed text-gray-300 to text-muted-foreground */}
              <div className="text-muted-foreground font-medium text-sm glow-text">AWS Certs</div>
            </div>
            <div className="text-center p-4 bg-blue-500/10 rounded-lg border border-blue-400/20 hover:border-blue-400/40 transition-all duration-300 hover-glow">
              <div className="text-2xl font-bold text-blue-400 mb-2 counter glow-text-strong">
                {certifications.filter(c => Array.isArray(c.category) ? c.category.includes('gcp') : c.category === 'gcp').length}
              </div>
              {/* ✨ MODIFIED: Changed text-gray-300 to text-muted-foreground */}
              <div className="text-muted-foreground font-medium text-sm glow-text">GCP Certs</div>
            </div>
            <div className="text-center p-4 bg-blue-600/10 rounded-lg border border-blue-500/20 hover:border-blue-500/40 transition-all duration-300 hover-glow">
              <div className="text-2xl font-bold text-blue-500 mb-2 counter glow-text-strong">
                {certifications.filter(c => Array.isArray(c.category) ? c.category.includes('azure') : c.category === 'azure').length}
              </div>
              {/* ✨ MODIFIED: Changed text-gray-300 to text-muted-foreground */}
              <div className="text-muted-foreground font-medium text-sm glow-text">Azure Certs</div>
            </div>
            <div className="text-center p-4 bg-gray-500/10 rounded-lg border border-gray-400/20 hover:border-gray-400/40 transition-all duration-300 hover-glow">
              <div className="text-2xl font-bold text-gray-300 mb-2 counter glow-text-strong">
                {certifications.filter(c => Array.isArray(c.category) ? c.category.includes('github') : c.category === 'github').length}
              </div>
              {/* ✨ MODIFIED: Changed text-gray-300 to text-muted-foreground */}
              <div className="text-muted-foreground font-medium text-sm glow-text">GitHub Certs</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CertificationsSection;
