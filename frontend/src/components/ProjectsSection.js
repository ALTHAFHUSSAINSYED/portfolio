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

  // Restore scroll if coming back
  useEffect(() => {
    if (location.state && location.state.scrollY) {
      window.scrollTo(0, location.state.scrollY);
    }
  }, [location]);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/projects`);
        if (!response.ok) throw new Error('Something went wrong fetching projects.');
        const data = await response.json();

        // Ensure arrays for safe mapping
        const processedData = data.map(proj => ({
          ...proj,
          summary: proj.summary ? proj.summary.split('\n') : [],
          key_outcomes: proj.key_outcomes || [],
          technologies: proj.technologies || [],
        }));

        setProjects(processedData);
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

  const getProjectColor = (index) => ['text-cyan-soft', 'text-pink-soft', 'text-green-soft'][index % 3];
  const getProjectBg = (index) => ['bg-cyan-400/10', 'bg-pink-500/10', 'bg-green-400/10'][index % 3];
  const getProjectBorder = (index) => ['border-cyan-400/30', 'border-pink-500/30', 'border-green-400/30'][index % 3];

  if (loading) {
    return (
      <section id="projects" className="py-20 bg-black flex justify-center items-center min-h-[50vh]">
        <div className="text-center text-white">
          <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-cyan-soft" />
          <p>Loading Projects...</p>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section id="projects" className="py-20 bg-black flex justify-center items-center min-h-[50vh]">
        <div className="text-center text-red-400">
          <AlertTriangle className="w-12 h-12 mx-auto mb-4" />
          <p>Error: {error}</p>
        </div>
      </section>
    );
  }

  return (
    <section id="projects" className="py-20 bg-black relative overflow-hidden" ref={sectionRef}>
      <div className="absolute inset-0 overflow-hidden">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16">
          <h2 className={`text-3xl md:text-4xl font-bold mb-4 shine-text ${isVisible ? 'fade-in-up' : ''}`}>
            Featured Projects
          </h2>
          <p className={`text-lg text-gray-300 max-w-3xl mx-auto glow-text ${isVisible ? 'fade-in-up stagger-1' : ''}`}>
            Real-world implementations showcasing expertise in cloud infrastructure and DevOps automation
          </p>
        </div>
        <div className="grid lg:grid-cols-3 gap-8">
          {projects.map((project, index) => (
            <Card
              key={project.id}
              className={`flex flex-col p-6 bg-black/80 border border-gray-700/30 hover:border-cyan-400/40 transition-all duration-500 backdrop-blur-sm neon-card hover-lift group ${isVisible ? `scale-in stagger-${index + 2}` : ''}`}
            >
              <div className="flex-grow">
                <div className="flex items-start space-x-4 mb-6">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 ${getProjectBg(index)} border ${getProjectBorder(index)} group-hover:scale-110 transition-all`}>
                    {React.createElement(getProjectIcon(project.name), { className: `w-6 h-6 ${getProjectColor(index)}` })}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-cyan-soft transition-all">{project.name}</h3>
                  </div>
                </div>

                {/* Multi-line summary with icon */}
                <div className="text-gray-300 mb-6 leading-relaxed glow-text space-y-2">
                  {project.summary.map((point, i) => (
                    <div key={i} className="flex items-start space-x-2">
                      <Zap className="w-4 h-4 mt-1 text-cyan-soft flex-shrink-0"/>
                      <p className="text-sm">{point}</p>
                    </div>
                  ))}
                </div>

                {/* Technologies */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-white mb-3">Technologies Used</h4>
                  <div className="flex flex-wrap gap-2">
                    {project.technologies.map((tech) => (
                      <Badge key={tech} variant="outline" className="border-cyan-400/30 text-cyan-soft bg-black/50">{tech}</Badge>
                    ))}
                  </div>
                </div>

                {/* Key Outcomes */}
                <div className="space-y-3 mb-6">
                  <h4 className="text-sm font-semibold text-white">Key Outcomes</h4>
                  <div className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">
                    {project.key_outcomes}
                  </div>
                </div>
              </div>

              <div className="pt-4 mt-auto border-t border-gray-700/30">
                <Link
                  to={`/projects/${project.id}`}
                  state={{ scrollY: window.scrollY }} // Pass current scroll position
                  className="flex items-center text-cyan-soft text-sm font-medium group-hover:text-cyan-400 transition-all"
                >
                  <span>View Implementation Details</span>
                  <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-2 transition-transform" />
                </Link>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default ProjectsSection;
