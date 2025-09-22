// src/components/ProjectDetailPage.js
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Loader2, AlertTriangle, ArrowLeft, CheckCircle, Code, Server, Folder, Zap } from 'lucide-react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://althaf-portfolio.onrender.com';

// Icon mapping functions
const getProjectIcon = (title) => {
  if (title.toLowerCase().includes('pipeline')) return Code;
  if (title.toLowerCase().includes('infrastructure')) return Server;
  if (title.toLowerCase().includes('storage')) return Folder;
  return Zap;
};

const summaryIcon = Zap;   // Icon for summary points
const detailsIcon = Code;  // Icon for details points

const ProjectDetailPage = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProjectDetails = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}`);
        if (!response.ok) throw new Error('Project not found or server error.');
        const data = await response.json();
        setProject({
          ...data,
          summary: data.summary ? data.summary.split('\n') : [],
          details: data.details ? data.details.split('\n') : [],
          key_outcomes: data.key_outcomes || [],
        });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchProjectDetails();
    window.scrollTo(0, 0);
  }, [projectId]);

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
        <button
          onClick={() => navigate(-1)}
          className="mt-4 text-cyan-soft"
        >
          Back
        </button>
      </div>
    );
  }

  const IconComponent = getProjectIcon(project.name);

  return (
    <div className="bg-black text-white min-h-screen font-sans py-20">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-12">
          <button
            onClick={() => {
              if (location.state && location.state.scrollY) {
                navigate('/', { state: { scrollY: location.state.scrollY } });
              } else {
                navigate('/');
              }
            }}
            className="inline-flex items-center text-cyan-soft hover:text-cyan-400 transition-colors group"
          >
            <ArrowLeft className="w-5 h-5 mr-2 transition-transform duration-300 group-hover:-translate-x-1" />
            Back to All Projects
          </button>
        </div>

        <Card className="p-6 sm:p-8 bg-black/80 border border-gray-700/30 backdrop-blur-sm neon-card">
          <div className="flex items-start space-x-4 mb-6">
            <div className="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 bg-cyan-400/10 border border-cyan-400/30">
              <IconComponent className="w-6 h-6 text-cyan-soft" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-white mb-2">{project.name}</h1>
            </div>
          </div>

          {/* Summary Section */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-white mb-3">Summary</h2>
            <div className="space-y-2">
              {project.summary.map((point, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <summaryIcon className="w-4 h-4 text-cyan-soft mt-1 flex-shrink-0"/>
                  <p className="text-gray-300 text-sm leading-relaxed">{point}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Image */}
          <div className="mb-8 rounded-lg overflow-hidden border border-gray-700/50">
            <img src={project.image_url} alt={project.name} className="w-full h-auto object-cover" />
          </div>

          {/* Technologies and Key Outcomes */}
          <div className="grid md:grid-cols-2 gap-8 mb-8">
            <div>
              <h2 className="text-lg font-semibold text-white mb-4">Technologies Used</h2>
              <div className="flex flex-wrap gap-2">
                {project.technologies.map((tech) => (
                  <Badge key={tech} variant="outline" className="border-cyan-400/30 text-cyan-soft bg-black/50">{tech}</Badge>
                ))}
              </div>
            </div>

            <div>
              <h2 className="text-lg font-semibold text-white mb-4">Key Outcomes</h2>
              <div className="space-y-3">
                {project.key_outcomes.map((outcome, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <CheckCircle className="w-4 h-4 text-green-soft mt-0.5 flex-shrink-0" />
                    <p className="text-gray-300 text-sm leading-relaxed">{outcome}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Details Section */}
          <div>
            <h2 className="text-lg font-semibold text-white mb-3">Implementation Details</h2>
            <div className="space-y-2">
              {project.details.map((point, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <detailsIcon className="w-4 h-4 text-purple-400 mt-1 flex-shrink-0"/>
                  <p className="text-gray-300 text-sm leading-relaxed">{point}</p>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default ProjectDetailPage;
