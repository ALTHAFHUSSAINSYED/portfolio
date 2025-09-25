import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Mail } from 'lucide-react';

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
      const response = await fetch(`${API_BASE_URL}/api/blogs/${blogId}`);
      if (!response.ok) throw new Error('Blog not found.');
      const data = await response.json();
      setBlog(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <p className="mt-4">Loading Blog Details...</p>;
  if (error) return <p className="mt-4 font-semibold text-red-500">{error}</p>;
  if (!blog) return null;

  return (
    <section className="py-20 bg-background text-foreground">
      <div className="max-w-3xl mx-auto px-4">
        <Card className="p-8 relative block-card">
          <div className="absolute top-4 right-4">
            <Mail className="w-6 h-6 text-cyan-400" />
          </div>
          <h1 className="text-3xl font-bold mb-6">{blog.title}</h1>
          <Badge className="mb-2">{blog.category || 'General'}</Badge>
          <div className="mt-4 text-lg text-muted-foreground whitespace-pre-line">{blog.content}</div>
        </Card>
      </div>
    </section>
  );
};

export default BlogDetailPage;
