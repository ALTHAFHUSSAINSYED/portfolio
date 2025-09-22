import React, { useEffect, useRef, useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Folder, CheckCircle, ArrowRight, Zap, Code, Server, Loader2, AlertTriangle } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://althaf-portfolio.onrender.com';

const ProjectsSection = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef(null);
  const location = useLocation();

  useEffect(() => {
    if (location.state && location.state.scrollPosition) {
      window.scrollTo(0, location.state.scrollPosition);
    }
  }, [location.state]);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/projects`);
        if (!response.ok) throw new Error('Something went wrong fetching projects.');
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

  const getProjectIcon = (title) => {
    if (title.toLowerCase().includes('pipeline')) return Code;
    if (title.toLowerCase().includes('infrastructure')) return Server;
    if (title.toLowerCase().includes('storage')) return Folder;
    return Zap;
  };

  if (loading || error) { /* ... loading/error JSX ... */ }

  return (
    <section id="projects" className="py-20 bg-black relative overflow-hidden" ref={sectionRef}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16"><h2 className={`text-3xl md:text-4xl font-bold mb-4 ${isVisible ? 'fade-in-up' : ''}`}>Featured Projects</h2></div>
        <div className="grid lg:grid-cols-3 gap-8">
          {projects.map((project, index) => {
            const IconComponent = getProjectIcon(project.name);
            return (
              <Card key={project.id} className={`flex flex-col p-6 bg-black/80 border border-gray-700/30 group ${isVisible ? `scale-in stagger-${index + 2}` : ''}`}>
                <div className="flex-grow">
                  <div className="flex items-start space-x-4 mb-6">
                    <div className="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 bg-cyan-400/10 border border-cyan-400/30">
                      <IconComponent className="w-6 h-6 text-cyan-soft" />
                    </div>
                    <div><h3 className="text-xl font-bold text-white">{project.name}</h3></div>
                  </div>
                  <p className="text-gray-300 mb-6 whitespace-pre-wrap">{project.summary}</p>
                  <div className="mb-6">
                    <h4 className="text-sm font-semibold text-white mb-3">Technologies Used</h4>
                    <div className="flex flex-wrap gap-2">{project.technologies.map((tech) => (<Badge key={tech} variant="outline" className="border-cyan-400/30 text-cyan-soft bg-black/50">{tech}</Badge>))}</div>
                  </div>
                  <div className="space-y-2 mb-6">
                    <h4 className="text-sm font-semibold text-white">Key Outcomes</h4>
                    {/* ✨ MODIFIED: Split outcomes into a list with checkmark icons */}
                    {project.key_outcomes.split('\n').filter(line => line.trim() !== '').map((outcome, idx) => (
                      <div key={idx} className="flex items-start space-x-3">
                        <CheckCircle className="w-4 h-4 text-green-soft mt-1 flex-shrink-0" />
                        <p className="text-gray-300 text-sm">{outcome}</p>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="pt-4 mt-auto border-t border-gray-700/30">
                  <Link to={`/projects/${project.id}`} state={{ scrollPosition: window.scrollY }} className="flex items-center text-cyan-soft text-sm font-medium">
                    <span>View Implementation Details</span>
                    <ArrowRight className="w-4 h-4 ml-2" />
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
