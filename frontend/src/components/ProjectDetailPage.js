// src/components/ProjectDetailPage.js
import React, { useState, useEffect } from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import { Loader2, AlertTriangle, ArrowLeft, CheckCircle, Zap } from 'lucide-react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://althaf-portfolio.onrender.com';

// Icons for summary and details
const SummaryIcon = Zap; // icon for summary bullet points
const DetailsIcon = Zap; // icon for details bullet points
const KeyOutcomeIcon = CheckCircle; // old icon for key outcomes

const ProjectDetailPage = () => {
  const { projectId } = useParams(); 
  const location = useLocation(); // for scroll position
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProjectDetails = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}`);
        if (!response.ok) throw new Error('Project not found or server error.');
        const data = await response.json();
        setProject(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchProjectDetails();
  }, [projectId]);

  // Scroll to previous position if coming back
  useEffect(() => {
    if (location.state && location.state.scrollY) {
      window.scrollTo({ top: location.state.scrollY, behavior: 'smooth' });
    }
  }, [location]);

  if (loading) {
    return (
      <div className="bg-black text-white min-h-screen flex justify-center items-center">
        <Loader2 className="w-12 h-12 animate-spin text-cyan-soft"/>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="bg-black text-white min-h-screen flex flex-col justify-center items-center">
        <AlertTriangle className="w-12 h-12 text-red-400"/>
        <p className="mt-4">Could not load project details.</p>
        <Link to="/" className="mt-4 text-cyan-soft">Back to Portfolio</Link>
      </div>
    );
  }

  // Helper to render multi-line text as bullets
  const renderTextWithBullets = (text, IconComponent) => {
    return text.split('\n').map((line, index) => (
      <div key={index} className="flex items-start space-x-3 mb-1">
        <IconComponent className="w-4 h-4 text-green-soft mt-1 flex-shrink-0" />
        <p className="text-gray-300 text-sm leading-relaxed">{line}</p>
      </div>
    ));
  };

  return (
    <div className="bg-black text-white min-h-screen font-sans py-20">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-12">
          <Link
            to="/"
            state={{ scrollY: location.state?.scrollY || 0 }} // send scrollY back
            className="inline-flex items-center text-cyan-soft hover:text-cyan-400 transition-colors group"
          >
            <ArrowLeft className="w-5 h-5 mr-2 transition-transform duration-300 group-hover:-translate-x-1" />
            Back to All Projects
          </Link>
        </div>

        <Card className="p-6 sm:p-8 bg-black/80 border border-gray-700/30 backdrop-blur-sm neon-card">
          <div className="flex items-start space-x-4 mb-6">
            <div className="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 bg-cyan-400/10 border border-cyan-400/30">
              {project.name.toLowerCase().includes('pipeline') ? <Zap className="w-6 h-6 text-cyan-soft" /> : <Zap className="w-6 h-6 text-cyan-soft" />}
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-white mb-2">{project.name}</h1>
            </div>
          </div>

          {/* Summary */}
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-white mb-3">Summary</h2>
            {renderTextWithBullets(project.summary, SummaryIcon)}
          </div>

          {/* Project Image */}
          <div className="mb-8 rounded-lg overflow-hidden border border-gray-700/50">
            <img src={project.image_url} alt={project.name} className="w-full h-auto object-cover" />
          </div>

          {/* Technologies */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-white mb-3">Technologies Used</h2>
            <div className="flex flex-wrap gap-2">
              {project.technologies.map((tech) => (
                <Badge key={tech} variant="outline" className="border-cyan-400/30 text-cyan-soft bg-black/50">{tech}</Badge>
              ))}
            </div>
          </div>

          {/* Details */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-white mb-3">Implementation Details</h2>
            {renderTextWithBullets(project.details, DetailsIcon)}
          </div>

          {/* Key Outcomes */}
          <div>
            <h2 className="text-lg font-semibold text-white mb-3">Key Outcomes</h2>
            {renderTextWithBullets(project.key_outcomes, KeyOutcomeIcon)}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default ProjectDetailPage;
