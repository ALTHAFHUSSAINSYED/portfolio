// src/components/ProjectsSection.js

import React, { useEffect, useRef, useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Folder, CheckCircle, ArrowRight, Zap, Code, Server, Loader2, AlertTriangle } from 'lucide-react';
import { Link } from 'react-router-dom';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://althaf-portfolio.onrender.com';

const ProjectsSection = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);

  // ✨ REMOVED: All manual scroll restoration logic (useEffect hooks related to location.state) is now gone.
  // The official <ScrollRestoration /> component in App.js will handle this automatically.

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/projects`);
        if (!response.ok) throw new Error('Something went wrong fetching projects.');
        const data = await response.json();
        setProjects(data);
      } catch (err) { setError(err.message); } 
      finally { setLoading(false); }
    };
    fetchProjects();
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsVisible(true);
        observer.unobserve(entry.target);
      }
    }, { threshold: 0.1 });
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => {
      if(sectionRef.current) {
        observer.unobserve(sectionRef.current);
      }
    };
  }, []);

  const getProjectIcon = (title) => {
    if (title.toLowerCase().includes('pipeline')) return Code;
    if (title.toLowerCase().includes('infrastructure')) return Server;
    if (title.toLowerCase().includes('storage')) return Folder;
    return Zap;
  };

  if (loading) {
    return (
      <section id="projects" className="py-20 bg-background text-foreground">
        <div className="text-center">
          <Loader2 className="w-8 h-8 mx-auto animate-spin" />
          <p className="mt-4">Loading Projects...</p>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section id="projects" className="py-20 bg-background text-destructive-foreground">
        <div className="text-center bg-destructive p-4 rounded-md max-w-md mx-auto">
          <AlertTriangle className="w-8 h-8 mx-auto" />
          <p className="mt-4 font-semibold">Error Loading Projects</p>
          <p className="text-sm">{error}</p>
        </div>
      </section>
    );
  }

  return (
    <section id="projects" className="py-20 bg-background" ref={sectionRef}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16"><h2 className={`text-3xl md:text-4xl font-bold mb-4 text-foreground ${isVisible ? 'fade-in-up' : ''}`}>Featured Projects</h2></div>
        <div className="grid lg:grid-cols-3 gap-8">
          {projects.map((project, index) => {
            const IconComponent = getProjectIcon(project.name);
            return (
              // ✨ MODIFIED: Added a min-height to prevent layout shift while content loads.
              <Card key={project.id} className={`flex flex-col p-6 neon-card group min-h-[520px] ${isVisible ? `scale-in stagger-${index + 2}` : ''}`}>
                <div className="flex-grow">
                  <div className="flex items-start space-x-4 mb-6">
                    <div className="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 bg-cyan-400/10 border border-cyan-400/30"><IconComponent className="w-6 h-6 text-cyan-soft" /></div>
                    <div><h3 className="text-xl font-bold text-foreground">{project.name}</h3></div>
                  </div>
                  
                  <div className="space-y-2 mb-6">
                    {(project.summary || '').split('\n').filter(line => line.trim() !== '').map((line, idx) => (
                      <div key={idx} className="flex items-start space-x-3">
                        <ArrowRight className="w-4 h-4 text-cyan-soft mt-1 flex-shrink-0" />
                        <p className="text-muted-foreground text-sm">{line}</p>
                      </div>
                    ))}
                  </div>

                  <div className="mb-6">
                    <h4 className="text-sm font-semibold text-foreground mb-3">Technologies Used</h4>
                    <div className="flex flex-wrap gap-2">{project.technologies.map((tech) => (<Badge key={tech} variant="outline" className="border-cyan-400/30 text-cyan-soft bg-background/50">{tech}</Badge>))}</div>
                  </div>
                  <div className="space-y-2 mb-6">
                    <h4 className="text-sm font-semibold text-foreground">Key Outcomes</h4>
                    {(project.key_outcomes || '').split('\n').filter(line => line.trim() !== '').map((outcome, idx) => (
                      <div key={idx} className="flex items-start space-x-3">
                        <CheckCircle className="w-4 h-4 text-green-soft mt-1 flex-shrink-0" />
                        <p className="text-muted-foreground text-sm">{outcome}</p>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="pt-4 mt-auto border-t border-border/30">
                  <Link to={`/projects/${project.id}`} className="flex items-center text-cyan-soft text-sm font-medium">
                    <span>View Implementation Details</span><ArrowRight className="w-4 h-4 ml-2" />
                  </Link>
                </div>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default ProjectsSection;
