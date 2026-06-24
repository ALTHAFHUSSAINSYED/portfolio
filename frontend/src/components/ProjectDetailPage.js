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
  // Exclude markdown headings
  if (trimmedLine.startsWith('# ') || trimmedLine.startsWith('## ') || trimmedLine.startsWith('### ')) {
    return false;
  }
  const codeKeywords = ['from', 'workdir', 'copy', 'run', 'env', 'cmd', 'pipeline', 'agent', 'stages', 'stage', 'steps', 'sh', 'docker', 'kubectl', 'helm', 'apiversion', 'kind', 'metadata', 'spec'];
  return (
    (trimmedLine.startsWith('#') && !trimmedLine.startsWith('# ')) || // shell comments
    codeKeywords.some(keyword => trimmedLine.toLowerCase().startsWith(keyword)) || 
    line.startsWith('    ') || 
    line.startsWith('\t')
  );
};

// Helper function to parse **bold** text in markdown
const parseBoldText = (text) => {
  if (!text) return "";
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} className="font-semibold text-foreground">{part.slice(2, -2)}</strong>;
    }
    return part;
  });
};

// Group lines into rich blocks (paragraphs, headings, lists, and code blocks)
const groupLines = (detailsText) => {
  const lines = (detailsText || '').split('\n');
  const blocks = [];
  let currentCodeBlock = null;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    if (isCodeLine(line)) {
      if (!currentCodeBlock) {
        currentCodeBlock = { type: 'code', lines: [] };
        blocks.push(currentCodeBlock);
      }
      currentCodeBlock.lines.push(line);
    } else {
      currentCodeBlock = null; // Reset code block
      
      if (trimmed.startsWith('### ')) {
        blocks.push({ type: 'h3', text: trimmed.replace('### ', '') });
      } else if (trimmed.startsWith('## ')) {
        blocks.push({ type: 'h2', text: trimmed.replace('## ', '') });
      } else if (trimmed.startsWith('# ')) {
        blocks.push({ type: 'h1', text: trimmed.replace('# ', '') });
      } else if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
        blocks.push({ type: 'bullet', text: trimmed.substring(2) });
      } else if (/^\d+\.\s/.test(trimmed)) {
        const match = trimmed.match(/^(\d+)\.\s(.*)/);
        blocks.push({ type: 'number', num: match[1], text: match[2] });
      } else if (trimmed === '') {
        blocks.push({ type: 'empty' });
      } else {
        blocks.push({ type: 'paragraph', text: line });
      }
    }
  }
  return blocks;
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
        
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-foreground mb-4 border-b border-border pb-2">Implementation Details</h2>
          <div className="space-y-4">
            {groupLines(project.details).map((block, idx) => {
              switch (block.type) {
                case 'h1':
                  return (
                    <h1 key={idx} className="text-2xl font-extrabold text-foreground mt-8 mb-4">
                      {parseBoldText(block.text)}
                    </h1>
                  );
                case 'h2':
                  return (
                    <h2 key={idx} className="text-xl font-bold text-foreground mt-7 mb-3 border-b border-border/50 pb-1">
                      {parseBoldText(block.text)}
                    </h2>
                  );
                case 'h3':
                  return (
                    <h3 key={idx} className="text-lg font-semibold text-cyan-soft mt-6 mb-2 flex items-center gap-2">
                      <Zap className="w-4 h-4 text-cyan-soft" />
                      {parseBoldText(block.text)}
                    </h3>
                  );
                case 'bullet':
                  return (
                    <div key={idx} className="flex items-start space-x-2 pl-2 text-muted-foreground my-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-soft mt-2 flex-shrink-0"></span>
                      <p className="text-sm leading-relaxed">{parseBoldText(block.text)}</p>
                    </div>
                  );
                case 'number':
                  return (
                    <div key={idx} className="flex items-start space-x-2 pl-2 text-muted-foreground my-1.5">
                      <span className="text-xs font-bold text-cyan-soft bg-cyan-soft/10 px-1.5 py-0.5 rounded flex-shrink-0 mt-0.5">
                        {block.num}
                      </span>
                      <p className="text-sm leading-relaxed">{parseBoldText(block.text)}</p>
                    </div>
                  );
                case 'code':
                  return (
                    <div key={idx} className="my-4 rounded-lg border border-border bg-slate-950 p-4 font-mono text-xs text-slate-200 overflow-x-auto shadow-md">
                      <div className="flex justify-between items-center text-[10px] text-slate-500 uppercase tracking-wider border-b border-slate-800 pb-2 mb-3">
                        <span className="flex items-center gap-1">
                          <Code className="w-3 h-3 text-cyan-soft" />
                          Configuration / Code Block
                        </span>
                      </div>
                      <pre className="whitespace-pre leading-relaxed">{block.lines.join('\n')}</pre>
                    </div>
                  );
                case 'paragraph':
                  return (
                    <p key={idx} className="text-sm leading-relaxed text-muted-foreground pl-1">
                      {parseBoldText(block.text)}
                    </p>
                  );
                case 'empty':
                default:
                  return <div key={idx} className="h-2"></div>;
              }
            })}
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
