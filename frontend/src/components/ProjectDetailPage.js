import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { ArrowLeft, Loader2, AlertTriangle, Zap, Code, CheckCircle } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://althaf-portfolio.onrender.com';

// Helper function to check if a line is a code example
const isCodeLine = (line) => {
  const trimmedLine = line.trim();
  const codeKeywords = ['FROM', 'WORKDIR', 'COPY', 'RUN', 'ENV', 'CMD', 'pipeline', 'agent', 'stages', 'stage', 'steps', 'sh', 'docker', 'kubectl', 'helm'];
  return trimmedLine.startsWith('#') || codeKeywords.some(keyword => trimmedLine.toLowerCase().startsWith(keyword)) || line.startsWith('    ') || trimmedLine.startsWith('-');
};

const ProjectDetailsPage = () => {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProject = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}`);
        if (!response.ok) throw new Error('Project not found.');
        const data = await response.json();
        setProject(data);
      } catch (err) { setError(err.message); } 
      finally { setLoading(false); }
    };
    fetchProject();
  }, [projectId]);

  const handleGoBack = () => {
    navigate(-1);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background text-foreground flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 mx-auto animate-spin" />
          <p className="mt-4">Loading Project Details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background text-destructive-foreground flex items-center justify-center p-4">
        <div className="text-center bg-destructive p-6 rounded-md max-w-md mx-auto">
          <AlertTriangle className="w-8 h-8 mx-auto" />
          <p className="mt-4 font-semibold">Error Loading Project</p>
          <p className="text-sm">{error}</p>
          <button onClick={handleGoBack} className="mt-4 flex items-center text-destructive-foreground underline mx-auto">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!project) {
    return null; // Render nothing until the project data is available
  }

  return (
    <div className="w-full max-w-4xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
      <button onClick={handleGoBack} className="flex items-center text-cyan-soft mb-8 hover:text-cyan-400 group transition-colors">
        <ArrowLeft className="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-transform" />
        Back to All Projects
      </button>

      <Card className="w-full p-8 neon-card">
        <h1 className="text-3xl font-bold text-foreground mb-6">{project.name}</h1>
        
        {project.image_url && (
          <div className="mb-8 w-full aspect-video bg-muted/50 rounded-lg overflow-hidden">
            {/* ✨ MODIFIED: Changed object-cover to object-contain to make the full image visible */}
            <img src={project.image_url} alt={project.name} className="w-full h-full object-contain"/>
          </div>
        )}

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-foreground mb-4">Summary</h2>
          <div className="space-y-2">
            {(project.summary || '').split('\n').filter(line => line.trim() !== '').map((line, idx) => (
              <div key={idx} className="flex items-start space-x-3 text-muted-foreground">
                <Zap className="w-4 h-4 text-blue-400 mt-1 flex-shrink-0" />
                <p>{line}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-foreground mb-4">Technologies Used</h2>
          <div className="flex flex-wrap gap-2">
            {(project.technologies || []).map((tech) => (<Badge key={tech} variant="outline" className="border-cyan-400/30 text-cyan-soft bg-background/50">{tech}</Badge>))}
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-semibold text-foreground mb-4">Key Outcomes</h2>
          <div className="space-y-2">
            {(project.key_outcomes || '').split('\n').filter(line => line.trim() !== '').map((line, idx) => (
              <div key={idx} className="flex items-start space-x-3 text-muted-foreground">
                <CheckCircle className="w-4 h-4 text-green-soft mt-1 flex-shrink-0" />
                <p>{line}</p>
              </div>
            ))}
          </div>
        </section>
        
        <section>
          <h2 className="text-xl font-semibold text-foreground mb-4">Implementation Details</h2>
          <div className="space-y-2">
            {(project.details || '').split('\n').map((line, idx) => (
              <div key={idx} className="flex items-start space-x-3 text-muted-foreground">
                {isCodeLine(line) || line.trim() === '' ? (
                  <div className="w-4 flex-shrink-0"></div>
                ) : (
                  <Code className="w-4 h-4 text-purple-400 mt-1 flex-shrink-0" />
                )}
                <p className="whitespace-pre-wrap font-mono text-sm break-words">{line}</p>
              </div>
            ))}
          </div>
        </section>
      </Card>
    </div>
  );
};

export default ProjectDetailsPage;
