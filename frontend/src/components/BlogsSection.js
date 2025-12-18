import React, { useState, useEffect, useRef } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Search, X, Calendar, ArrowRight, Tag, AlertCircle } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.althafportfolio.site';

const BlogsSection = () => {
  // STATE MANAGEMENT
  const [blogs, setBlogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [isVisible, setIsVisible] = useState(false);
  
  const sectionRef = useRef(null);
  const navigate = useNavigate();
  const location = useLocation();

  // 1. ANIMATION OBSERVER
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setIsVisible(true);
      },
      { threshold: 0.1 }
    );
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => {
        if (sectionRef.current) observer.unobserve(sectionRef.current);
    };
  }, []);

  // 2. FETCH DATA (Load all blogs once)
  useEffect(() => {
    const fetchBlogs = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/blogs`);
        if (!response.ok) throw new Error('Failed to fetch blogs');
        const data = await response.json();
        setBlogs(data);
      } catch (error) {
        console.error('Error fetching blogs:', error);
        // Fallback to local data
        try {
            const localData = await import('../../public/data/blogs.json');
            setBlogs(localData.default || []);
        } catch (e) {
            setBlogs([]);
        }
      } finally {
        setLoading(false);
      }
    };
    fetchBlogs();
  }, []);

  // 3. SYNC URL TO STATE (Handle browser back/forward and external links)
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const categoryParam = params.get('category');
    if (categoryParam) {
      setSelectedCategory(categoryParam);
      // Only scroll if we are not already there (optional)
      const section = document.getElementById('blogs');
      if (section && window.scrollY < section.offsetTop) {
        section.scrollIntoView({ behavior: 'smooth' });
      }
    }
  }, [location.search]);

  // 4. EXTRACT CATEGORIES (Static List)
  // FIX: Derived from ALL blogs, not filtered ones, so they don't disappear while searching
  const categories = [...new Set(blogs.flatMap(blog => 
    blog.category ? [blog.category] : []
  ))].sort();

  // 5. SEARCH & FILTER ENGINE
  const filteredBlogs = blogs.filter(blog => {
    // Normalize query
    const query = searchQuery.toLowerCase().trim();
    
    // A. Search Check (Title OR Summary OR Tags) - Case Insensitive
    const matchesSearch = !query || 
      (blog.title && blog.title.toLowerCase().includes(query)) ||
      (blog.summary && blog.summary.toLowerCase().includes(query)) ||
      (blog.tags && blog.tags.some(tag => tag.toLowerCase().includes(query)));

    // B. Category Check
    const matchesCategory = !selectedCategory || blog.category === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  // 6. ACTIONS
  const clearFilters = () => {
    setSearchQuery('');           // Clear text
    setSelectedCategory(null);    // Clear category
    navigate('/', { replace: true }); // Clear URL params
  };

  const handleCategoryClick = (category) => {
    if (selectedCategory === category) {
      // Toggle off if already selected
      clearFilters();
    } else {
      // Set new category
      setSelectedCategory(category);
      setSearchQuery(''); // Optional: Clear search text when picking a category for clarity
      navigate(`/?category=${encodeURIComponent(category)}`, { replace: true });
    }
  };

  return (
    // UI: "Neon/Cyberpunk" Style (Old UI Preserved)
    <section id="blogs" className="py-20 bg-background relative overflow-hidden" ref={sectionRef}>
      {/* Background Orbs */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Header */}
        <div className="text-center mb-12">
          <h2 className={`text-3xl md:text-4xl font-bold mb-4 shine-text ${isVisible ? 'fade-in-up' : ''}`}>
            Technical Insights
          </h2>
          <p className={`text-lg text-muted-foreground max-w-2xl mx-auto glow-text ${isVisible ? 'fade-in-up stagger-1' : ''}`}>
            Exploring the frontiers of DevOps, Cloud Computing, and AI.
          </p>
        </div>

        {/* Search & Filter Controls */}
        <div className={`mb-12 space-y-8 ${isVisible ? 'fade-in-up stagger-2' : ''}`}>
          
          {/* Search Bar - Neon/Glass Style */}
          <div className="max-w-xl mx-auto relative group">
            <div className="absolute inset-0 bg-cyan-400/20 rounded-xl blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-muted-foreground group-hover:text-cyan-soft transition-colors" />
              <Input
                type="text"
                placeholder="Search articles (e.g., 'DevOps', 'AWS', 'Security')..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-12 pr-10 py-6 bg-background/50 backdrop-blur-md border-cyan-400/30 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 text-lg rounded-xl transition-all shadow-lg neon-border"
              />
              {searchQuery && (
                <button 
                  onClick={() => setSearchQuery('')}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-red-400 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>
          </div>

          {/* Categories Buttons - Always Visible */}
          <div className="flex flex-wrap justify-center gap-3">
            <Button
              variant={selectedCategory === null ? "default" : "outline"}
              onClick={() => handleCategoryClick(null)}
              className={`rounded-full px-6 transition-all duration-300 ${
                selectedCategory === null 
                  ? 'neon-button bg-gradient-to-r from-cyan-500 to-blue-500 text-white border-0 font-bold shadow-[0_0_15px_rgba(34,211,238,0.5)]' 
                  : 'bg-background/50 border-border/50 text-muted-foreground hover:border-cyan-400 hover:text-cyan-soft hover:shadow-[0_0_10px_rgba(34,211,238,0.2)]'
              }`}
            >
              All Topics
            </Button>
            
            {/* Map Categories */}
            {categories.map((cat) => (
              <Button
                key={cat}
                variant={selectedCategory === cat ? "default" : "outline"}
                onClick={() => handleCategoryClick(cat)}
                className={`rounded-full px-5 transition-all duration-300 ${
                  selectedCategory === cat 
                    ? 'neon-button bg-gradient-to-r from-pink-500 to-purple-500 text-white border-0 font-bold shadow-[0_0_15px_rgba(236,72,153,0.5)]' 
                    : 'bg-background/50 border-border/50 text-muted-foreground hover:border-pink-400 hover:text-pink-soft hover:shadow-[0_0_10px_rgba(236,72,153,0.2)]'
                }`}
              >
                {cat}
              </Button>
            ))}

            {/* Clear All Button - Visible if ANY filter is active */}
            {(selectedCategory || searchQuery) && (
                <Button
                    variant="ghost"
                    onClick={clearFilters}
                    className="text-red-400 hover:text-red-300 hover:bg-red-400/10 rounded-full px-4 transition-colors"
                >
                    <X className="w-4 h-4 mr-1" /> Clear Filters
                </Button>
            )}
          </div>
        </div>

        {/* Results Grid */}
        {loading ? (
          <div className="text-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mx-auto mb-4 shadow-[0_0_15px_rgba(34,211,238,0.5)]"></div>
            <p className="text-muted-foreground glow-text">Loading articles...</p>
          </div>
        ) : filteredBlogs.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredBlogs.map((blog, index) => (
              <Card 
                key={blog._id || blog.id} 
                className={`flex flex-col h-full overflow-hidden transition-all duration-500 backdrop-blur-sm neon-card hover-lift group border-border/40 ${isVisible ? `rotate-in stagger-${(index % 3) + 3}` : ''}`}
              >
                {/* Blog Image */}
                <div className="h-48 bg-gradient-to-br from-gray-900 to-black relative overflow-hidden group-hover:opacity-90 transition-opacity">
                  <div className="absolute inset-0 bg-grid-white/[0.05] bg-[length:20px_20px]" />
                  <div className="absolute top-4 left-4">
                    <Badge className="bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 backdrop-blur-md shadow-[0_0_10px_rgba(34,211,238,0.3)]">
                      {blog.category || 'Tech'}
                    </Badge>
                  </div>
                </div>

                {/* Blog Content */}
                <div className="p-6 flex flex-col flex-grow relative z-10">
                  <div className="flex items-center text-xs text-muted-foreground mb-4 space-x-4">
                    <span className="flex items-center text-cyan-soft/80">
                      <Calendar className="w-3 h-3 mr-1" />
                      {new Date(blog.createdAt || blog.date).toLocaleDateString()}
                    </span>
                    <span className="flex items-center text-pink-soft/80">
                      <Tag className="w-3 h-3 mr-1" />
                      {blog.tags ? blog.tags.length : 0} tags
                    </span>
                  </div>

                  <h3 className="text-xl font-bold mb-3 text-foreground line-clamp-2 group-hover:text-cyan-soft transition-colors duration-300 shine-text-slow">
                    {blog.title}
                  </h3>
                  
                  <p className="text-muted-foreground text-sm mb-6 line-clamp-3 flex-grow glow-text">
                    {blog.summary}
                  </p>

                  <div className="mt-auto pt-4 border-t border-white/10 flex justify-between items-center">
                    <a 
                      href={`/blog/${blog._id || blog.id}`} 
                      className="text-sm font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 hover:to-purple-500 transition-all flex items-center group-hover:translate-x-1 duration-300"
                    >
                      Read Article <ArrowRight className="w-4 h-4 ml-2 text-cyan-400" />
                    </a>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          /* Empty State */
          <div className="text-center py-20 bg-secondary/10 rounded-2xl border border-dashed border-cyan-400/30 backdrop-blur-sm neon-card">
            <AlertCircle className="w-12 h-12 text-cyan-soft mx-auto mb-4 opacity-50 shadow-[0_0_15px_rgba(34,211,238,0.3)] rounded-full" />
            <h3 className="text-xl font-bold text-foreground mb-2 shine-text">No articles found</h3>
            <p className="text-muted-foreground mb-6 glow-text">
              We couldn't find any matches for "{searchQuery}"
              {selectedCategory && ` in ${selectedCategory}`}.
            </p>
            <Button 
              onClick={clearFilters}
              variant="outline"
              className="border-pink-500/50 text-pink-400 hover:bg-pink-500/10 hover:text-pink-300 hover:shadow-[0_0_10px_rgba(236,72,153,0.3)] transition-all"
            >
              Clear all filters
            </Button>
          </div>
        )}
      </div>
    </section>
  );
};

export default BlogsSection;
