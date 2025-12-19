import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Newspaper, ArrowLeft, Calendar, Tag, ExternalLink } from 'lucide-react';
import { Button } from './ui/button';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.althafportfolio.site';

const BlogDetailPage = () => {
  const { blogId } = useParams();
  const navigate = useNavigate();
  const [blog, setBlog] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showFullContent, setShowFullContent] = useState(true);

  useEffect(() => {
    fetchBlog();
    // eslint-disable-next-line
  }, [blogId]);

  const fetchBlog = async () => {
    setLoading(true);
    try {
      // FAST: Load directly from local blogs.json for instant performance
      const localRes = await fetch('/data/blogs.json');
      if (!localRes.ok) {
        throw new Error('Failed to load blogs data');
      }
      
      const data = await localRes.json();
      // Extract blogs array from the response (handle both {blogs: [...]} and [...] formats)
      const allBlogs = Array.isArray(data) ? data : (data.blogs || []);
      const blog = allBlogs.find(b => b.id === blogId || b._id === blogId);
      
      if (blog) {
        setBlog(blog);
        setError(null);
      } else {
        throw new Error('Blog not found');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Helper function to convert markdown to HTML (simple version)
  const renderMarkdown = (content) => {
    if (!content) return '';
    
    // Handle paragraphs
    const withParagraphs = content
      .split('\n\n')
      .map(para => `<p>${para.trim()}</p>`)
      .join('');
    
    // Handle headers
    const withHeaders = withParagraphs
      .replace(/## (.*?)$/gm, '<h2 class="text-2xl font-bold my-4">$1</h2>')
      .replace(/# (.*?)$/gm, '<h1 class="text-3xl font-bold my-4">$1</h1>')
      .replace(/### (.*?)$/gm, '<h3 class="text-xl font-bold my-3">$1</h3>');
    
    // Handle bold and italics
    const withFormatting = withHeaders
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-gray-100 dark:bg-gray-800 px-1 rounded">$1</code>');
    
    // Handle lists
    const withLists = withFormatting
      .replace(/^\s*-\s+(.*?)$/gm, '<li>$1</li>')
      .replace(/(<li>.*?<\/li>\n)+/g, '<ul class="list-disc pl-5 my-3">$&</ul>');
    
    return withLists;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="min-h-screen flex flex-col justify-center items-center">
        <div className="bg-red-100 dark:bg-red-900/20 p-6 rounded-lg max-w-md text-center">
          <p className="font-semibold text-red-500 dark:text-red-400 mb-4">{error}</p>
          <Button asChild variant="outline">
            <Link to="/"><ArrowLeft className="mr-2 h-4 w-4" /> Back to Home</Link>
          </Button>
        </div>
      </div>
    );
  }
  
  if (!blog) return null;

  // SEO meta data
  const siteUrl = 'https://www.althafportfolio.site';
  const blogUrl = `${siteUrl}/blogs/${blog.id}`;
  const imageUrl = blog.imageUrl || `${siteUrl}/profile-pic.jpg`;
  const description = blog.summary || blog.topic || 'Read this article on Althaf Hussain\'s portfolio';
  const keywords = blog.tags ? blog.tags.join(', ') : 'software engineering, tech blog';
  const publishedDate = blog.created_at ? new Date(blog.created_at).toISOString() : new Date().toISOString();
  
  // Extract plain text from markdown for JSON-LD
  const contentPreview = blog.content 
    ? blog.content.replace(/[#*`_\[\]]/g, '').substring(0, 200) 
    : description;

  return (
    <>
      <Helmet>
        {/* Primary Meta Tags */}
        <title>{blog.title} | Althaf Hussain</title>
        <meta name="title" content={blog.title} />
        <meta name="description" content={description} />
        <meta name="keywords" content={keywords} />
        <meta name="author" content="Althaf Hussain" />
        
        {/* Open Graph / Facebook */}
        <meta property="og:type" content="article" />
        <meta property="og:url" content={blogUrl} />
        <meta property="og:title" content={blog.title} />
        <meta property="og:description" content={description} />
        <meta property="og:image" content={imageUrl} />
        <meta property="article:published_time" content={publishedDate} />
        <meta property="article:author" content="Althaf Hussain" />
        {blog.tags && blog.tags.map((tag, idx) => (
          <meta key={`og-tag-${idx}`} property="article:tag" content={tag} />
        ))}
        
        {/* Twitter */}
        <meta property="twitter:card" content="summary_large_image" />
        <meta property="twitter:url" content={blogUrl} />
        <meta property="twitter:title" content={blog.title} />
        <meta property="twitter:description" content={description} />
        <meta property="twitter:image" content={imageUrl} />
        
        {/* Canonical URL */}
        <link rel="canonical" href={blogUrl} />
        
        {/* JSON-LD Structured Data for SEO */}
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": blog.title,
            "description": description,
            "image": imageUrl,
            "datePublished": publishedDate,
            "dateModified": publishedDate,
            "author": {
              "@type": "Person",
              "name": "Althaf Hussain Syed",
              "jobTitle": "DevOps Engineer | Cloud Architect",
              "url": siteUrl,
              "sameAs": [
                "https://www.linkedin.com/in/althafhussainsyed/",
                "https://github.com/ALTHAFHUSSAINSYED"
              ]
            },
            "publisher": {
              "@type": "Person",
              "name": "Althaf Hussain Syed",
              "logo": {
                "@type": "ImageObject",
                "url": `${siteUrl}/profile-pic.jpg`
              }
            },
            "mainEntityOfPage": {
              "@type": "WebPage",
              "@id": blogUrl
            },
            "keywords": keywords,
            "articleBody": contentPreview
          })}
        </script>
      </Helmet>
      
      <section className="py-20 bg-background text-foreground">
        <div className="max-w-4xl mx-auto px-4">
          <button
            className="inline-flex items-center text-primary hover:text-primary/80 mb-6 font-semibold border border-primary rounded px-4 py-2 bg-background"
            onClick={() => {
              // Pass state to teleport directly to blogs section
              navigate('/', { state: { scrollTo: 'blogs' } });
            }}
          >
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to all blogs
          </button>
        
        <Card className="p-8 relative block-card shadow-lg">
          {/* Header Section */}
          <div className="absolute top-4 right-4">
            <Newspaper className="w-6 h-6 text-cyan-400" />
          </div>
          
          <h1 className="text-4xl font-bold mb-4">{blog.title}</h1>
          
          {/* Author Byline */}
          <div className="mb-6 pb-6 border-b border-border">
            <div className="flex items-center gap-3 mb-3">
              <img 
                src="/profile-pic.jpg" 
                alt="Althaf Hussain Syed"
                className="w-12 h-12 rounded-full border-2 border-primary"
              />
              <div>
                <p className="text-lg font-semibold text-foreground">Althaf Hussain Syed</p>
                <p className="text-sm text-muted-foreground">DevOps Engineer | Cloud Architect</p>
              </div>
            </div>
            <div className="flex items-center text-sm text-muted-foreground">
              <Calendar className="mr-2 h-4 w-4" />
              <span className="font-medium">Published:</span>
              <span className="ml-2">
                {blog.created_at && new Date(blog.created_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </span>
            </div>
          </div>
          
          {/* Meta Information */}
          <div className="flex flex-wrap gap-2 mb-6">
            
            <div className="flex flex-wrap gap-2">
              {blog.category && (
                <Badge variant="default" className="flex items-center bg-primary text-primary-foreground mr-2">
                  <Tag className="mr-1 h-3 w-3" /> {blog.category}
                </Badge>
              )}
              {blog.tags && blog.tags.map((tag, idx) => (
                <Badge key={idx} variant="secondary" className="flex items-center">
                  <Tag className="mr-1 h-3 w-3" /> {tag}
                </Badge>
              ))}
            </div>
          </div>
          
          {/* Summary Section */}
          {blog.summary && (
            <div className="bg-secondary/20 p-4 rounded-md mb-8">
              <h2 className="text-xl font-semibold mb-2">Overview</h2>
              <p className="italic">{blog.summary}</p>
            </div>
          )}

          {/* Table of Contents if blog has sections */}
          {blog.sections && blog.sections.length > 0 && (
            <div className="bg-secondary/10 p-4 rounded-md mb-8">
              <h2 className="text-xl font-semibold mb-3">Table of Contents</h2>
              <ul className="list-none space-y-2">
                {blog.sections.map((section, idx) => (
                  <li key={idx} className="flex items-center">
                    <span className="mr-2 text-primary">{idx + 1}.</span>
                    <a href={`#section-${idx}`} className="text-primary hover:underline">
                      {section.title}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Main Content */}
          <div className="mt-6 prose dark:prose-invert max-w-none">
            {blog.content ? (
              <div 
                className="
                  [&_p]:text-lg [&_p]:text-gray-800 dark:[&_p]:text-gray-300 [&_p]:leading-relaxed [&_p]:mb-6
                  [&_li]:text-lg [&_li]:text-gray-800 dark:[&_li]:text-gray-300
                  [&_h1]:text-3xl [&_h1]:text-gray-900 dark:[&_h1]:text-white [&_h1]:mb-6
                  [&_h2]:text-2xl [&_h2]:text-cyan-600 dark:[&_h2]:text-cyan-400 [&_h2]:mt-10 [&_h2]:mb-4
                  [&_h3]:text-xl [&_h3]:text-pink-600 dark:[&_h3]:text-pink-400 [&_h3]:mt-8 [&_h3]:mb-3
                  [&_strong]:text-gray-900 dark:[&_strong]:text-white
                "
                dangerouslySetInnerHTML={{ __html: renderMarkdown(blog.content) }} 
              />
            ) : (
              <div className="text-red-500 font-semibold">Full blog content is not available for this entry.</div>
            )}
          </div>
          
          {/* Technologies Used Section */}
          {blog.technologies && blog.technologies.length > 0 && (
            <div className="mt-8 pt-6 border-t border-border">
              <h3 className="text-lg font-semibold mb-3">Technologies & Tools Used</h3>
              <div className="flex flex-wrap gap-2">
                {blog.technologies.map((tech, idx) => (
                  <Badge key={idx} variant="outline" className="bg-secondary/20">
                    {tech}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Code Examples Section */}
          {blog.codeExamples && blog.codeExamples.length > 0 && (
            <div className="mt-8 pt-6 border-t border-border">
              <h3 className="text-lg font-semibold mb-3">Code Examples</h3>
              {blog.codeExamples.map((example, idx) => (
                <div key={idx} className="mb-4">
                  <h4 className="text-md font-medium mb-2">{example.title}</h4>
                  <pre className="bg-secondary/20 p-4 rounded-md overflow-x-auto">
                    <code>{example.code}</code>
                  </pre>
                </div>
              ))}
            </div>
          )}

          {/* Key Takeaways Section */}
          {blog.keyTakeaways && blog.keyTakeaways.length > 0 && (
            <div className="mt-8 pt-6 border-t border-border">
              <h3 className="text-lg font-semibold mb-3">Key Takeaways</h3>
              <ul className="list-disc list-inside space-y-2">
                {blog.keyTakeaways.map((takeaway, idx) => (
                  <li key={idx} className="text-muted-foreground">{takeaway}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Author Bio Section */}
          <div className="mt-12 pt-8 border-t-2 border-primary/30">
            <div className="bg-secondary/30 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-4 text-foreground">About the Author</h3>
              <div className="flex flex-col md:flex-row gap-6">
                <div className="flex-shrink-0">
                  <img 
                    src="/profile-pic.jpg" 
                    alt="Althaf Hussain Syed"
                    className="w-24 h-24 rounded-full border-4 border-primary"
                  />
                </div>
                <div className="flex-1">
                  <h4 className="text-lg font-semibold mb-2">Althaf Hussain Syed</h4>
                  <p className="text-sm text-primary font-medium mb-3">DevOps Engineer | AWS Solutions Architect | Cloud Infrastructure Specialist</p>
                  <p className="text-muted-foreground leading-relaxed mb-4">
                    Althaf Hussain Syed is a DevOps Engineer with 3.5+ years of experience building scalable cloud infrastructure 
                    and automation solutions for enterprise clients. Currently working as Analyst III Infrastructure Services at DXC Technology, 
                    he specializes in AWS cloud architecture, CI/CD automation, and containerized deployments using Docker and Kubernetes.
                  </p>
                  <p className="text-muted-foreground leading-relaxed mb-4">
                    He holds multiple cloud certifications including AWS Solutions Architect Associate, AWS AI Practitioner, 
                    Google Cloud Professional Architect, and Azure Administrator Associate. His work focuses on reducing manual 
                    effort through end-to-end automation (achieving 70% efficiency improvements) and implementing enterprise-grade 
                    DevOps practices aligned with ITIL and SDLC frameworks.
                  </p>
                  <p className="text-muted-foreground leading-relaxed mb-4">
                    Creator of the <strong>Change-Cost Integration Model (CCIM)</strong> framework for enterprise integration strategy. 
                    Recognized with multiple DXC CHAMPS Awards for operational excellence and consistent delivery of critical infrastructure services.
                  </p>
                  <div className="flex gap-4 mt-4">
                    <a 
                      href="https://www.linkedin.com/in/althafhussainsyed/" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-primary hover:text-primary/80 text-sm font-medium flex items-center gap-1"
                    >
                      <ExternalLink className="h-4 w-4" />
                      LinkedIn
                    </a>
                    <a 
                      href="https://github.com/ALTHAFHUSSAINSYED" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-primary hover:text-primary/80 text-sm font-medium flex items-center gap-1"
                    >
                      <ExternalLink className="h-4 w-4" />
                      GitHub
                    </a>
                    <a 
                      href="mailto:allualthaf42@gmail.com"
                      className="text-primary hover:text-primary/80 text-sm font-medium flex items-center gap-1"
                    >
                      <ExternalLink className="h-4 w-4" />
                      Email
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* References and Sources */}
          {blog.sources && blog.sources.length > 0 && (
            <div className="mt-8 pt-6 border-t border-border">
              <h3 className="text-lg font-semibold mb-3">References & Resources</h3>
              <ul className="list-disc list-inside space-y-2">
                {blog.sources.map((source, idx) => (
                  <li key={idx} className="text-sm text-muted-foreground">
                    <a 
                      href={source} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-primary hover:underline inline-flex items-center"
                    >
                      {new URL(source).hostname.replace('www.', '')}
                      <ExternalLink className="ml-1 h-3 w-3" />
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Copyright Notice */}
          <div className="mt-8 pt-6 border-t border-border text-center">
            <p className="text-sm text-muted-foreground">
              © {new Date(blog.created_at || Date.now()).getFullYear()} Althaf Hussain Syed. Original content. 
              <span className="block mt-1">Unauthorized reproduction prohibited.</span>
            </p>
          </div>
        </Card>
      </div>
    </section>
    </>
  );
};

export default BlogDetailPage;
