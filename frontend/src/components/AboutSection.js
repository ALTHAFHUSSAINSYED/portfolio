import React, { useEffect, useRef, useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Award, TrendingUp, Shield, Zap, X } from 'lucide-react';
import IntroductionVideo from './IntroductionVideo';
import { LazyLoadImage } from 'react-lazy-load-image-component';
import 'react-lazy-load-image-component/src/effects/blur.css';

const AboutSection = ({ personalInfo, achievements, education }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [hoveredSkill, setHoveredSkill] = useState(null);
  const [selectedAward, setSelectedAward] = useState(null);
  const sectionRef = useRef(null);

  const iconMap = {
    'DXC CHAMPS Award – FY24 Q1': Award,
    'DXC CHAMPS Award – FY26 H1': Award,
    'Multi-Cloud Certified Professional': Shield,
    'CI/CD Automation Excellence': TrendingUp,
    'RAG Pipeline & AI Assistant Development': Zap
  };

  const iconColors = {
    'DXC CHAMPS Award – FY24 Q1': 'text-yellow-soft',
    'DXC CHAMPS Award – FY26 H1': 'text-yellow-soft',
    'Multi-Cloud Certified Professional': 'text-pink-soft',
    'CI/CD Automation Excellence': 'text-cyan-soft',
    'RAG Pipeline & AI Assistant Development': 'text-purple-soft'
  };


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

    return () => observer.disconnect();
  }, []);

  // Disable body scroll when modal is open
  useEffect(() => {
    if (selectedAward) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    // Cleanup on unmount
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [selectedAward]);


  return (
    // ✨ MODIFIED: Changed gradient to be theme-aware
    <section id="about" className="pt-8 pb-20 bg-gradient-to-b from-background to-secondary relative overflow-hidden" ref={sectionRef}>
      {/* Animated background effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="absolute top-1/4 right-1/4 w-1 h-1 bg-cyan-400 rounded-full floating opacity-30"></div>
        <div className="absolute bottom-1/3 left-1/3 w-2 h-2 bg-pink-500 rounded-full bounce-slow opacity-20"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16">
          <h1 className="text-3xl md:text-4xl font-bold mb-6 text-gray-900 dark:text-white shine-text">
            About Me - DevOps Engineer & Cloud Infrastructure Engineer
          </h1>
          <div className="max-w-4xl mx-auto text-lg text-gray-700 dark:text-muted-foreground leading-relaxed">
            <p className="mb-4">
              Passionate DevOps engineer specializing in cloud infrastructure and automation solutions
            </p>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Professional Summary */}
          <div className={`space-y-6 ${isVisible ? 'fade-in-left stagger-2' : ''}`}>
            <h3 className="text-2xl font-semibold mb-4 attractive-text">
              <span className="text-cyan-soft">Professional</span> <span className="text-pink-soft">Summary</span>
            </h3>
            {/* ✨ MODIFIED: Changed text-gray-300 to text-muted-foreground */}
            <p className="text-muted-foreground leading-relaxed text-lg mb-8">
              {personalInfo.summary}
            </p>

            {/* Education Block */}
            {education && (
              <div className="space-y-4 mb-8">
                <h4 className="text-lg font-semibold text-foreground">Education:</h4>
                <div className="grid gap-3">
                  {education.map((edu, index) => (
                    <div
                      key={index}
                      className={`p-3 rounded-lg border border-border/30 bg-background/40 backdrop-blur-sm transition-all duration-300 hover:border-cyan-400/30 group ${isVisible ? `fade-in-up stagger-${index + 2}` : ''}`}
                    >
                      <div className="flex items-start gap-3">
                        {/* University Logo */}
                        <div className="flex-shrink-0 w-12 h-12 rounded-lg overflow-hidden bg-white/90 p-1 flex items-center justify-center">
                          <LazyLoadImage
                            src="/assets/anu.png"
                            alt="Acharya Nagarjuna University - B.Tech Computer Science and Engineering"
                            effect="blur"
                            className="w-full h-full object-contain"
                            width={48}
                            height={48}
                          />
                        </div>

                        {/* Education Details */}
                        <div className="flex-1 flex justify-between items-start">
                          <div>
                            <h5 className="text-sm font-semibold text-cyan-soft group-hover:text-cyan-400 transition-colors">
                              {edu.degree}
                            </h5>
                            <p className="text-xs text-muted-foreground mt-1">{edu.institution}</p>
                          </div>
                          <span className="text-sm font-medium text-cyan-soft dark:text-cyan-400 bg-background/40 dark:bg-background/60 backdrop-blur-sm px-3 py-1.5 rounded-lg border border-border/30 whitespace-nowrap ml-3">
                            {edu.duration}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="space-y-4">
              {/* ✨ MODIFIED: Changed text-white to text-foreground */}
              <h4 className="text-lg font-semibold text-foreground">Key Expertise Areas:</h4>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { name: 'Cloud Infrastructure Engineering', color: 'cyan' },
                  { name: 'DevOps Automation', color: 'pink' },
                  { name: 'CI/CD Pipelines', color: 'green' },
                  { name: 'Infrastructure as Code', color: 'yellow' },
                  { name: 'Container Orchestration', color: 'blue' },
                  { name: 'SDLC/ITIL/DevOps Operations', color: 'purple' }
                ].map((skill, index) => (
                  <div
                    key={skill.name}
                    onMouseEnter={() => setHoveredSkill(skill.name)}
                    onMouseLeave={() => setHoveredSkill(null)}
                    className={`border px-3 py-2 rounded-md text-sm font-medium transition-all duration-300 backdrop-blur-sm cursor-default ${hoveredSkill === skill.name
                      ? `border-${skill.color}-400/50 text-${skill.color}-soft bg-${skill.color}-400/10 scale-105`
                      : 'border-border/30 text-muted-foreground bg-background/50'
                      } ${isVisible ? `fade-in-up stagger-${index + 3}` : ''}`}
                  >
                    {skill.name}
                  </div>
                ))}
              </div>

              {/* Introduction Video */}
              <div className="mt-6">
                <IntroductionVideo />
              </div>
            </div>
          </div>

          {/* Key Achievements */}
          <div className={`space-y-6 ${isVisible ? 'fade-in-right stagger-3' : ''}`}>
            <h3 className="text-2xl font-semibold mb-6 attractive-text">
              <span className="text-pink-soft">Key</span> <span className="text-cyan-soft">Achievements</span>
            </h3>
            <div className="space-y-4">
              {achievements.map((achievement, index) => {
                const IconComponent = iconMap[achievement.title] || Award;
                const iconColor = iconColors[achievement.title] || 'text-cyan-soft';
                return (
                  // ✨ MODIFIED: Removed redundant/conflicting color classes to let neon-card work
                  <Card
                    key={index}
                    className={`p-6 transition-all duration-300 group backdrop-blur-sm neon-card hover-lift ${isVisible ? `fade-in-up stagger-${index + 4}` : ''
                      }`}
                  >
                    <div className="flex items-start space-x-4">
                      {/* Achievement Icon/Logo */}
                      <div className={`flex-shrink-0 w-12 h-12 ${achievement.title.includes('DXC CHAMPS') ? 'bg-white' : 'bg-secondary/50'} rounded-lg flex items-center justify-center group-hover:bg-secondary/80 transition-all duration-300 border border-border/20 hover-rotate overflow-hidden`}>
                        {achievement.title.includes('DXC CHAMPS') ? (
                          <img
                            src={achievement.title.includes('FY26 H1') ? '/assets/dxc-award-fy26h1.png' : '/assets/dxc-award.png'}
                            alt="DXC CHAMPS Award Certificate"
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <IconComponent className={`w-6 h-6 ${iconColor}`} />
                        )}
                      </div>
                      <div className="flex-1">
                        {/* ✨ MODIFIED: Changed text-white to text-foreground */}
                        <h4 className="font-semibold text-foreground mb-2 group-hover:text-cyan-soft transition-colors duration-300">
                          {achievement.title}
                        </h4>
                        {/* ✨ MODIFIED: Changed text-gray-300 to text-muted-foreground */}
                        <p className="text-muted-foreground leading-relaxed mb-3">
                          {achievement.description}
                        </p>
                        {/* View Award Button */}
                        {achievement.awardUrl && (
                          <button
                            onClick={() => setSelectedAward(achievement)}
                            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-cyan-soft hover:text-cyan-400 bg-secondary/50 hover:bg-secondary/80 border border-cyan-400/30 hover:border-cyan-400/60 rounded-lg transition-all duration-300 hover:scale-105"
                          >
                            <Award className="w-4 h-4" />
                            View Award
                          </button>
                        )}
                        {achievement.awardUrl === null && achievement.title.includes('FY26') && (
                          <button
                            disabled
                            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-muted-foreground bg-secondary/30 border border-border/20 rounded-lg cursor-not-allowed opacity-50"
                          >
                            <Award className="w-4 h-4" />
                            View Award (Coming Soon)
                          </button>
                        )}
                      </div>
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        </div>

        {/* Personal Touch */}
        {/* ✨ MODIFIED: Removed redundant/conflicting color classes to let neon-card work */}
        <div className={`mt-16 text-center rounded-xl p-8 backdrop-blur-sm neon-card hover-lift transition-all duration-300 ${isVisible ? 'slide-in-bottom stagger-6' : ''
          }`}>
          {/* ✨ MODIFIED: Changed text-white to text-foreground */}
          <h3 className="text-xl font-semibold text-foreground mb-4">
            <span className="text-green-soft">Why I Love</span> <span className="text-blue-soft">DevOps</span>
          </h3>
          {/* ✨ MODIFIED: Changed text-gray-300 to text-muted-foreground */}
          <p className="text-muted-foreground max-w-3xl mx-auto text-lg leading-relaxed">
            I'm passionate about bridging the gap between development and operations, creating robust,
            scalable systems that enable teams to deliver value faster and more reliably. Every
            automation script, every pipeline optimization, and every infrastructure improvement
            is an opportunity to make technology work better for people.
          </p>
        </div>

        {/* Award Modal */}
        {selectedAward && selectedAward.awardUrl && (
          <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
            onClick={() => setSelectedAward(null)}
          >
            <div
              className="relative max-w-4xl w-full bg-background rounded-xl shadow-2xl overflow-hidden border border-cyan-400/30"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Close Button */}
              <button
                onClick={() => setSelectedAward(null)}
                className="absolute top-4 right-4 z-10 w-10 h-10 flex items-center justify-center bg-background/90 hover:bg-background border border-border/50 hover:border-cyan-400/50 rounded-full transition-all duration-300 hover:scale-110"
                aria-label="Close award modal"
              >
                <X className="w-5 h-5 text-foreground" />
              </button>

              {/* Award Title */}
              <div className="bg-gradient-to-r from-cyan-500/10 to-pink-500/10 border-b border-border/30 px-6 py-4">
                <h3 className="text-xl font-semibold text-foreground flex items-center gap-2">
                  <Award className="w-6 h-6 text-yellow-soft" />
                  {selectedAward.title}
                </h3>
              </div>

              {/* Award Image */}
              <div className="p-6 bg-secondary/20">
                <img
                  src={selectedAward.awardUrl}
                  alt={selectedAward.title}
                  className="w-full h-auto rounded-lg shadow-lg"
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default AboutSection;
