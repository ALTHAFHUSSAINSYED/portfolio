// src/components/ProjectsSection.js (Corrected)
import React, { useEffect, useRef, useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Folder, CheckCircle, ArrowRight, Zap, Code, Server, Loader2, AlertTriangle } from 'lucide-react';
import { Link } from 'react-router-dom'; // Import Link for navigation

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://althaf-portfolio.onrender.com'; // Use your actual URL

const ProjectsSection = () => {
  const [projects, setProjects]       = useState([]);
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState(null);
  const [isVisible, setIsVisible]   = useState(false);
  const sectionRef                    = useRef(null);
  
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/projects`);
        if (!response.ok) {
          throw new Error('Something went wrong fetching the projects.');
        }
        const data = await response.json();
        setProjects(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
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
    return () => observer.disconnect();
  }, []);

  // Helper functions (getProjectIcon, etc.) remain the same
  const getProjectIcon = (title) => {
    if (title.toLowerCase().includes('pipeline')) return Code;
    if (title.toLowerCase().includes('infrastructure')) return Server;
    if (title.toLowerCase().includes('storage')) return Folder;
    return Zap;
  };
  const getProjectColor = (index) => ['text-cyan-soft', 'text-pink-soft', 'text-green-soft'][index % 3];
  const getProjectBg = (index) => ['bg-cyan-400/10', 'bg-pink-500/10', 'bg-green-400/10'][index % 3];
  const getProjectBorder = (index) => ['border-cyan-400/30', 'border-pink-500/30', 'border-green-400/30'][index % 3];
  
  if (loading) {
    return (
      <section id="projects" className="py-20 bg-black flex justify-center items-center min-h-[50vh]">
        <div className="text-center text-white"><Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-cyan-soft" /><p>Loading Projects...</p></div>
      </section>
    );
  }

  if (error) {
    return (
      <section id="projects" className="py-20 bg-black flex justify-center items-center min-h-[50vh]">
        <div className="text-center text-red-400"><AlertTriangle className="w-12 h-12 mx-auto mb-4" /><p>Error: {error}</p></div>
      </section>
    );
  }

  return (
    <section id="projects" className="py-20 bg-black relative overflow-hidden" ref={sectionRef}>
      <div className="absolute inset-0 overflow-hidden">
        <div className="bg-orb bg-orb-1"></div><div className="bg-orb bg-orb-2"></div><div className="bg-orb bg-orb-3"></div>
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16">
          <h2 className={`text-3xl md:text-4xl font-bold mb-4 shine-text ${isVisible ? 'fade-in-up' : ''}`}>Featured Projects</h2>
          <p className={`text-lg text-gray-300 max-w-3xl mx-auto glow-text ${isVisible ? 'fade-in-up stagger-1' : ''}`}>
            Real-world implementations showcasing expertise in cloud infrastructure and DevOps automation
          </p>
        </div>
        <div className="grid lg:grid-cols-3 gap-8">
          {projects.map((project, index) => {
            const IconComponent = getProjectIcon(project.name);
            const projectColor = getProjectColor(index);
            const projectBg = getProjectBg(index);
            const projectBorder = getProjectBorder(index);
            return (
              <Card key={project.id} className={`p-6 bg-black/80 border border-gray-700/30 hover:border-cyan-400/40 transition-all duration-500 backdrop-blur-sm neon-card hover-lift hover-shine group ${isVisible ? `scale-in stagger-${index + 2}` : ''}`}>
                <div className="flex items-start space-x-4 mb-6">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 ${projectBg} border ${projectBorder} group-hover:scale-110 transition-all duration-300 hover-rotate`}>
                    <IconComponent className={`w-6 h-6 ${projectColor} pulse-shine`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-cyan-soft transition-all duration-300 shine-text-slow">{project.name}</h3>
                  </div>
                </div>
                {/* ✨ MODIFIED: Changed project.description to project.summary */}
                <p className="text-gray-300 mb-6 leading-relaxed glow-text">{project.summary}</p>
                <div className="pt-4 border-t border-gray-700/30">
                  {/* ✨ MODIFIED: Changed <a> to <Link> for smoother navigation */}
                  <Link to={`/projects/${project.id}`} className="flex items-center text-cyan-soft text-sm font-medium group-hover:text-cyan-400 transition-all duration-300 cursor-pointer hover-glow p-2 rounded sparkle-text">
                    <span>View Implementation Details</span>
                    <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-2 transition-transform duration-300" />
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
