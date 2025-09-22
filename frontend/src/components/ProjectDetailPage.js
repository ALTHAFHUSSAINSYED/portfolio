import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { CheckCircle, ArrowLeft, Loader2, AlertTriangle } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://althaf-portfolio.onrender.com';

const ProjectDetailsPage = () => {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProject = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}`);
        if (!response.ok) throw new Error('Project not found.');
        const data = await response.json();
        setProject(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchProject();
  }, [projectId]);

  if (loading) {
    return (
      <div className="min-h-screen flex justify-center items-center bg-black">
        <Loader2 className="w-12 h-12 animate-spin text-cyan-soft" />
        <p className="text-white ml-4">Loading Project...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex justify-center items-center bg-black">
        <AlertTriangle className="w-12 h-12 text-red-400" />
        <p className="text-red-400 ml-4">{error}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black py-16 px-4 sm:px-6 lg:px-8">
      <Link to="/projects" className="flex items-center text-cyan-soft mb-8 hover:text-cyan-400 transition-all">
        <ArrowLeft className="w-5 h-5 mr-2" />
        Back to Projects
      </Link>

      <Card className="max-w-4xl mx-auto p-8 bg-black/80 border border-gray-700/30 backdrop-blur-sm">
        <h1 className="text-3xl font-bold text-white mb-4">{project.name}</h1>

        {project.image_url && (
          <div className="mb-6">
            <img
              src={project.image_url}
              alt={project.name}
              className="w-full h-auto rounded-md border border-gray-700/30"
            />
          </div>
        )}

        {/* Summary */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold text-white mb-2">Summary</h2>
          <div className="text-gray-300 leading-relaxed space-y-2">
            {project.summary.split('\n').map((line, idx) => (
              <p key={idx} className="flex items-start">
                <CheckCircle className="w-4 h-4 mt-1 mr-2 text-green-400 flex-shrink-0" />
                {line}
              </p>
            ))}
          </div>
        </section>

        {/* Details */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold text-white mb-2">Details</h2>
          <div className="text-gray-300 leading-relaxed space-y-2">
            {project.details.split('\n').map((line, idx) => (
              <p key={idx} className="flex items-start">
                <CheckCircle className="w-4 h-4 mt-1 mr-2 text-green-400 flex-shrink-0" />
                {line}
              </p>
            ))}
          </div>
        </section>

        {/* Technologies */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold text-white mb-2">Technologies Used</h2>
          <div className="flex flex-wrap gap-2">
            {project.technologies.map((tech) => (
              <Badge key={tech} variant="outline" className="border-cyan-400/30 text-cyan-soft bg-black/50">
                {tech}
              </Badge>
            ))}
          </div>
        </section>

        {/* Key Outcomes */}
        <section className="mb-6">
          <h2 className="text-xl font-semibold text-white mb-2">Key Outcomes</h2>
          <div className="text-gray-300 whitespace-pre-wrap">{project.key_outcomes}</div>
        </section>
      </Card>
    </div>
  );
};

export default ProjectDetailsPage;
