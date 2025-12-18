import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
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
      // Try ChromaDB API first
      let data = null;
      let succeeded = false;
      try {
        const chromaRes = await fetch(`/api/chromadb/blogs/${blogId}`);
        if (chromaRes.ok) {
          data = await chromaRes.json();
          succeeded = true;
        }
      } catch (err) {
        console.log(`Error fetching from ChromaDB: ${err.message}`);
      }
      // Fallback to MongoDB if ChromaDB fails
      if (!succeeded) {
        const baseUrls = [
          '',
          'https://althaf-portfolio.onrender.com',
          'https://althaf-portfolio.vercel.app',
          'http://localhost:5000'
        ];
        for (const baseUrl of baseUrls) {
          try {
            const response = await fetch(`${baseUrl}/api/blogs/${blogId}`);
            if (response.ok) {
              data = await response.json();
              succeeded = true;
              break;
            }
          } catch (err) {
            console.log(`Error fetching from ${baseUrl}: ${err.message}`);
          }
        }
      }
      
      // Final fallback: Load from local blogs.json file
      if (!succeeded) {
        try {
          const localRes = await fetch('/data/blogs.json');
          if (localRes.ok) {
            const allBlogs = await localRes.json();
            data = allBlogs.find(b => b.id === blogId || b._id === blogId);
            if (data) {
              succeeded = true;
              console.log('Loaded blog from local blogs.json');
            }
          }
        } catch (err) {
          console.log(`Error loading from local blogs.json: ${err.message}`);
        }
      }
      
      if (succeeded && data) {
        setBlog(data);
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

  return (
    <section className="py-20 bg-background text-foreground">
      <div className="max-w-4xl mx-auto px-4">
        <button
          className="inline-flex items-center text-primary hover:text-primary/80 mb-6 font-semibold border border-primary rounded px-4 py-2 bg-background"
          onClick={() => {
            // Smooth scroll to blogs section
            navigate('/');
            setTimeout(() => {
              const blogsSection = document.getElementById('blogs');
              if (blogsSection) {
                blogsSection.scrollIntoView({ behavior: 'smooth' });
              }
            }, 100);
          }}
        >
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to all blogs
        </button>
        
        <Card className="p-8 relative block-card shadow-lg">
          {/* Header Section */}
          <div className="absolute top-4 right-4">
            <Newspaper className="w-6 h-6 text-cyan-400" />
          </div>
          
          <h1 className="text-4xl font-bold mb-6">{blog.title}</h1>
          
          {/* Meta Information */}
          <div className="flex flex-wrap gap-2 mb-6">
            <div className="flex items-center text-sm text-muted-foreground">
              <Calendar className="mr-1 h-4 w-4" />
              {blog.created_at && new Date(blog.created_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </div>
            
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
          <div className="mt-6 prose prose-lg dark:prose-invert max-w-none">
            {blog.content ? (
              <div dangerouslySetInnerHTML={{ __html: renderMarkdown(blog.content) }} />
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

          {/* Author Info */}
          {blog.author && (
            <div className="mt-8 pt-6 border-t border-border flex items-center">
              <img 
                src={blog.author.avatar || "/profile-pic.jpg"} 
                alt={blog.author.name}
                className="w-12 h-12 rounded-full mr-4"
              />
              <div>
                <h3 className="text-lg font-semibold">{blog.author.name}</h3>
                <p className="text-sm text-muted-foreground">{blog.author.bio}</p>
              </div>
            </div>
          )}
        </Card>
      </div>
    </section>
  );
};

export default BlogDetailPage;
