import React, { useEffect, useRef, useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Mail } from 'lucide-react';
import { Link } from 'react-router-dom';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://althaf-portfolio.onrender.com';

const BlogsSection = () => {
  const [blogs, setBlogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const sectionRef = useRef(null);

  useEffect(() => {
    fetchBlogs();
  }, []);

  const fetchBlogs = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/blogs`);
      if (!response.ok) throw new Error('Failed to fetch blogs');
      const data = await response.json();
      setBlogs(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this blog?')) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/blogs/${id}`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Failed to delete blog');
      fetchBlogs();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <section id="blogs" className="py-20 bg-background relative overflow-hidden" ref={sectionRef}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Blogs</h2>
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
            Explore my latest blog posts and updates.
          </p>
        </div>
        {loading ? (
          <p className="mt-4">Loading Blogs...</p>
        ) : error ? (
          <p className="mt-4 font-semibold text-red-500">{error}</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {blogs.map((blog, idx) => (
              <Card key={blog._id || idx} className="p-8 relative block-card">
                <div className="absolute top-4 right-4">
                  <Mail className="w-6 h-6 text-cyan-400" />
                </div>
                <h3 className="text-xl font-bold mb-2">{blog.title}</h3>
                <p className="text-muted-foreground mb-4">{blog.summary}</p>
                <Badge className="mb-2">{blog.category || 'General'}</Badge>
                <div className="flex gap-2 mt-4">
                  <Button size="sm" variant="outline" onClick={() => { setEditBlog(blog); setShowForm(true); }}>Edit</Button>
                  <Button size="sm" variant="destructive" onClick={() => handleDelete(blog._id)}>Delete</Button>
                  <Link to={`/blogs/${blog._id}`} className="ml-auto text-cyan-500 underline">View</Link>
                </div>
              </Card>
            ))}
          </div>
        )}
        <div className="mt-8 text-center">
          <button className="glassmorphic-btn">See All Blogs</button>
        </div>
      </div>
    </section>
  );
};

export default BlogsSection;
