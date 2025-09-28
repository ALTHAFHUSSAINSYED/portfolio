import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Newspaper, ArrowLeft, Calendar, Tag, ExternalLink } from 'lucide-react';
import { Button } from './ui/button';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://althaf-portfolio.onrender.com';

const BlogDetailPage = () => {
  const { blogId } = useParams();
  const [blog, setBlog] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchBlog();
    // eslint-disable-next-line
  }, [blogId]);

  const fetchBlog = async () => {
    setLoading(true);
    try {
      // Try different API endpoints if the main one fails
      const baseUrls = [
        '', // Same domain (relative URL)
        'https://althaf-portfolio.onrender.com',
        'https://althaf-portfolio.vercel.app',
        'http://localhost:5000'
      ];
      
      let data = null;
      let succeeded = false;
      
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
      
      if (succeeded && data) {
        setBlog(data);
        setError(null);
      } else {
        throw new Error('Failed to fetch blog from all endpoints');
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
        <Link to="/" className="inline-flex items-center text-primary hover:text-primary/80 mb-6">
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Home
        </Link>
        
        <Card className="p-8 relative block-card shadow-lg">
          <div className="absolute top-4 right-4">
            <Newspaper className="w-6 h-6 text-cyan-400" />
          </div>
          
          <h1 className="text-4xl font-bold mb-6">{blog.title}</h1>
          
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
          
          {blog.summary && (
            <div className="bg-secondary/20 p-4 rounded-md mb-8 italic">
              {blog.summary}
            </div>
          )}
          
          <div 
            className="mt-6 prose prose-lg dark:prose-invert max-w-none"
            dangerouslySetInnerHTML={{ __html: renderMarkdown(blog.content) }}
          />
          
          {blog.sources && blog.sources.length > 0 && (
            <div className="mt-8 pt-6 border-t border-border">
              <h3 className="text-lg font-medium mb-2">Sources</h3>
              <ul className="list-disc list-inside">
                {blog.sources.map((source, idx) => (
                  <li key={idx} className="text-sm text-muted-foreground mb-1">
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
        </Card>
      </div>
    </section>
  );
};

export default BlogDetailPage;
