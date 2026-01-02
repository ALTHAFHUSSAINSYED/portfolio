import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import SEO from './SEO';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { ArrowLeft, Loader2, AlertTriangle, Zap, Code, CheckCircle, Newspaper } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.althafportfolio.site';

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
  const [relatedBlogs, setRelatedBlogs] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProject = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}`);
        if (!response.ok) throw new Error('Project not found.');
        const data = await response.json();
        setProject(data);
        
        // Fetch related blogs
        try {
          const blogsResponse = await fetch(`${API_BASE_URL}/api/blogs`);
          if (blogsResponse.ok) {
            const blogs = await blogsResponse.json();
            // Get first 3 blogs as related
            setRelatedBlogs(blogs.slice(0, 3));
          }
        } catch (err) {
          console.error("Error fetching related blogs:", err);
        }
      } catch (err) { setError(err.message); } 
      finally { setLoading(false); }
    };
    fetchProject();
  }, [projectId]);

  const handleGoBack = () => {
    // Pass state to teleport directly to projects section
    navigate('/', { state: { scrollTo: 'projects' } });
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

  // Generate SEO data for project
  const projectTitle = `${project.name} | Althaf Hussain Portfolio`;
  const projectDescription = project.summary 
    ? project.summary.split('\n').filter(line => line.trim()).join(' ').substring(0, 160)
    : `DevOps project: ${project.name}. Explore implementation details, technologies used, and key outcomes.`;
  const projectKeywords = [
    'DevOps Project',
    project.name,
    ...(project.technologies || []),
    'Cloud Computing',
    'Infrastructure Automation'
  ].join(', ');
  const projectUrl = `https://althafportfolio.site/projects/${projectId}`;
  const projectImage = project.image_url || 'https://althafportfolio.site/profile-pic.jpg';

  const projectStructuredData = {
    "@context": "https://schema.org",
    "@type": "CreativeWork",
    "name": project.name,
    "description": projectDescription,
    "image": projectImage,
    "url": projectUrl,
    "author": {
      "@type": "Person",
      "name": "Althaf Hussain Syed",
      "url": "https://althafportfolio.site"
    },
    "keywords": projectKeywords,
    "inLanguage": "en-US",
    "isPartOf": {
      "@type": "WebSite",
      "name": "Althaf Hussain Portfolio",
      "url": "https://althafportfolio.site"
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
      <SEO
        title={projectTitle}
        description={projectDescription}
        keywords={projectKeywords}
        url={projectUrl}
        image={projectImage}
        type="article"
        structuredData={projectStructuredData}
      />
      <button onClick={handleGoBack} className="flex items-center text-cyan-soft mb-8 hover:text-cyan-400 group transition-colors">
        <ArrowLeft className="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-transform" />
        Back to All Projects
      </button>

      <Card className="w-full p-8 neon-card">
        <h1 className="text-3xl font-bold text-foreground mb-6">{project.name}</h1>
        
        {/* ✨ MODIFIED: Removed the container div to allow the image to use its natural dimensions */}
        {project.image_url && (
          <img src={project.image_url} alt={project.name} className="w-full h-auto rounded-lg mb-8"/>
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

        {/* Related Blogs Section */}
        {relatedBlogs.length > 0 && (
          <section className="mt-8 pt-6 border-t border-border">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-foreground">
              <Newspaper className="w-5 h-5 text-cyan-soft" />
              Related DevOps & Cloud Blogs
            </h2>
            <div className="grid gap-4">
              {relatedBlogs.map((blog) => (
                <Link
                  key={blog.id}
                  to={`/blogs/${blog.id}`}
                  className="block p-4 rounded-lg border border-border hover:border-cyan-400/50 transition-colors group"
                >
                  <h3 className="font-semibold text-foreground group-hover:text-cyan-soft transition-colors mb-2">
                    {blog.title}
                  </h3>
                  <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
                    {blog.description || blog.summary || 'Read more about this topic'}
                  </p>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Badge variant="outline" className="text-xs">
                        {blog.category || 'DevOps'}
                      </Badge>
                    </span>
                    {blog.created_at && (
                      <span>
                        {new Date(blog.created_at).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric'
                        })}
                      </span>
                    )}
                  </div>
                </Link>
              ))}
            </div>
            <div className="mt-4">
              <Link
                to="/#blogs"
                className="text-cyan-soft hover:text-cyan-400 text-sm font-medium inline-flex items-center gap-1"
              >
                View All Blogs →
              </Link>
            </div>
          </section>
        )}
      </Card>
    </div>
  );
};

export default ProjectDetailsPage;
