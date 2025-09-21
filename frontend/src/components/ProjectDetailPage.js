// src/components/ProjectDetailPage.js

import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Loader2, AlertTriangle, ArrowLeft } from 'lucide-react';

// You must update this URL to match the one in your ProjectsSection.js file
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-backend-url.onrender.com';

const ProjectDetailPage = () => {
  // Get the project ID from the URL (e.g., "some-unique-id")
  const { projectId } = useParams(); 
  
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProjectDetails = async () => {
      try {
        // Fetch data from your backend API using the project ID
        const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}`);
        if (!response.ok) {
          throw new Error('Project not found or server error.');
        }
        const data = await response.json();
        setProject(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProjectDetails();
    
    // Scroll to the top of the page on load
    window.scrollTo(0, 0);

  }, [projectId]); // This effect runs every time the projectId in the URL changes

  if (loading) {
    return (
      <div className="bg-black text-white min-h-screen flex flex-col justify-center items-center">
        <Loader2 className="w-12 h-12 animate-spin text-cyan-soft mb-4" />
        <h1 className="text-2xl font-bold">Loading Project Details...</h1>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="bg-black text-white min-h-screen flex flex-col justify-center items-center text-center px-4">
        <AlertTriangle className="w-12 h-12 text-red-400 mb-4" />
        <h1 className="text-2xl font-bold text-red-400">Error</h1>
        <p className="text-gray-300 mt-2">Could not load the project details. Please try again later.</p>
        <Link to="/" className="mt-6 inline-flex items-center px-4 py-2 border border-cyan-400/50 text-cyan-soft rounded-md hover:bg-cyan-400/10 transition-colors">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Portfolio
        </Link>
      </div>
    );
  }

  return (
    <div className="bg-black text-white min-h-screen font-sans">
       <div className="relative isolate overflow-hidden">
        {/* Animated background elements */}
        <div className="absolute inset-0 z-0 overflow-hidden">
          <div className="bg-orb bg-orb-1 opacity-50"></div>
          <div className="bg-orb bg-orb-2 opacity-50"></div>
          <div className="bg-orb bg-orb-3 opacity-50"></div>
        </div>

        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32 relative z-10">
          {/* Back to Home Link */}
          <div className="mb-12">
            <Link to="/" className="inline-flex items-center text-cyan-soft hover:text-cyan-400 transition-colors group">
              <ArrowLeft className="w-5 h-5 mr-2 transition-transform duration-300 group-hover:-translate-x-1" />
              Back to All Projects
            </Link>
          </div>

          {/* Project Header */}
          <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight hero-title">
            {project.name}
          </h1>
          <p className="text-lg md:text-xl text-gray-300 mb-12 leading-relaxed">
            {project.description}
          </p>

          {/* Project Image */}
          <div className="mb-12 rounded-xl overflow-hidden border border-gray-700/50 shadow-2xl shadow-cyan-500/10">
            <img 
              src={project.image_url} 
              alt={project.name} 
              className="w-full h-auto object-cover" 
            />
          </div>

          {/* You can add more detailed sections here if you add more data to your database */}
          <div className="prose prose-invert prose-lg max-w-none text-gray-300">
            {/* Example of where more details could go */}
            <h2 className="text-3xl font-bold text-white border-b border-gray-700 pb-2">Implementation Overview</h2>
            <p>
              This section can contain more in-depth paragraphs about the project's architecture, challenges,
              and solutions. You can add new fields to your backend `Project` model (like `detailed_description`, `technologies`, etc.)
              and display them here.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectDetailPage;
