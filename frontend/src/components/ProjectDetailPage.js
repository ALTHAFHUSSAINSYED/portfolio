import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import SEO from './SEO';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { ArrowLeft, Loader2, AlertTriangle, Zap, Code, CheckCircle, Newspaper, Calendar, CheckCircle2, Terminal, AlertCircle, Cpu, Shield, Sparkles } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.althafportfolio.site';

// Helper function to check if a line is a code example
const isCodeLine = (line) => {
  const trimmedLine = line.trim();
  // Exclude markdown headings
  if (trimmedLine.startsWith('# ') || trimmedLine.startsWith('## ') || trimmedLine.startsWith('### ')) {
    return false;
  }
  // Check if it's a code block marker
  if (trimmedLine.startsWith('```')) {
    return true;
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
      return <strong key={i} className="font-semibold text-gray-900 dark:text-white">{part.slice(2, -2)}</strong>;
    }
    return part;
  });
};

// Helper function to recursively strip ALL bullet-like prefixes, emojis, and symbols from the start of a list item
const cleanAllBulletPrefixes = (text) => {
  let trimmed = (text || '').trim();
  
  // Strip standard markdown/plain bullet prefixes (repeatable)
  const bulletRegex = /^([-*•▪▫◦⬡○●■□▲▼◆◇👉]\s*)+/;
  trimmed = trimmed.replace(bulletRegex, '').trim();
  
  // Strip common bullet emojis/symbols
  const emojiRegex = /^(✔️|✅|✔|☑️|☑|⚠️|🚨|🔥|⚙️|🛠️|🔧|☸️|🐳|📦|🚀|⚡|🎯|🏆|🔹|🔷|▪️|▫️|👉)\s*/;
  trimmed = trimmed.replace(emojiRegex, '').trim();
  
  return trimmed;
};

// Identify the icon type and clean the text of starting symbols
const parseBulletLine = (text) => {
  let trimmed = (text || '').trim();
  
  // 1. First strip standard markdown/plain bullet prefixes
  const bulletRegex = /^([-*•▪▫◦⬡○●■□▲▼◆◇👉]\s*)+/;
  trimmed = trimmed.replace(bulletRegex, '').trim();
  
  // 2. Identify the icon type based on leading emojis or keywords
  let iconType = 'default';
  
  // Check for checkmarks / success
  if (trimmed.startsWith('✔️') || trimmed.startsWith('✅') || trimmed.startsWith('✔') || trimmed.startsWith('☑️') || trimmed.startsWith('☑')) {
    iconType = 'success';
  } 
  // Check for warning / alert / important
  else if (trimmed.startsWith('⚠️') || trimmed.startsWith('🚨') || trimmed.startsWith('🔥')) {
    iconType = 'warning';
  }
  // Check for tech / tools / engineering
  else if (trimmed.startsWith('⚙️') || trimmed.startsWith('🛠️') || trimmed.startsWith('🔧') || trimmed.startsWith('☸️') || trimmed.startsWith('🐳') || trimmed.startsWith('📦')) {
    iconType = 'tech';
  }
  // Check for actions / performance / speed / rocket
  else if (trimmed.startsWith('🚀') || trimmed.startsWith('⚡') || trimmed.startsWith('🎯') || trimmed.startsWith('🏆')) {
    iconType = 'action';
  }
  // Check for generic blue/cyan diamond or square
  else if (trimmed.startsWith('🔹') || trimmed.startsWith('🔷') || trimmed.startsWith('▪️') || trimmed.startsWith('▫️')) {
    iconType = 'bullet-cyan';
  }
  
  // 3. Clean all bullet and emoji prefixes from the text
  const cleanedText = cleanAllBulletPrefixes(trimmed);
  
  return {
    text: cleanedText,
    iconType
  };
};

// Group lines into rich blocks (paragraphs, headings, lists, and code blocks)
const groupLines = (detailsText) => {
  const lines = (detailsText || '').split('\n');
  const blocks = [];
  let currentCodeBlock = null;

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    let trimmed = line.trim();

    // Preprocess: Strip decorative emoji followed by keycap emoji (e.g. "📈 6️⃣" -> "6️⃣")
    // This resolves character corruption of decorative emojis and allows proper heading classification.
    const headingEmojiRegex = /^([^\s0-9🔟]+)\s+([0-9🔟]\ufe0f?\u20e3|1\ufe0f\u20e31\ufe0f\u20e3)/;
    if (headingEmojiRegex.test(trimmed)) {
      trimmed = trimmed.replace(headingEmojiRegex, '$2');
      line = trimmed;
    }

    if (trimmed === '') {
      if (currentCodeBlock) {
        currentCodeBlock.lines.push('');
      } else {
        blocks.push({ type: 'empty' });
      }
      continue;
    }

    // Handle code blocks marked with triple backticks
    if (trimmed.startsWith('```')) {
      if (currentCodeBlock) {
        currentCodeBlock = null; // End of code block
      } else {
        const lang = trimmed.substring(3).trim();
        currentCodeBlock = { type: 'code', lang: lang || 'config', lines: [] };
        blocks.push(currentCodeBlock);
      }
      continue;
    }

    if (currentCodeBlock) {
      currentCodeBlock.lines.push(line);
      continue;
    }

    // 1. Markdown headings
    if (trimmed.startsWith('# ')) {
      blocks.push({ type: 'h1', text: cleanAllBulletPrefixes(trimmed.replace('# ', '')) });
    } else if (trimmed.startsWith('## ')) {
      blocks.push({ type: 'h2', text: cleanAllBulletPrefixes(trimmed.replace('## ', '')) });
    } else if (trimmed.startsWith('### ')) {
      blocks.push({ type: 'h3', text: cleanAllBulletPrefixes(trimmed.replace('### ', '')) });
    } 
    // 2. Keycap emoji headings (e.g., 1️⃣ Architecture Overview, 1\ufe0f\u20e3 Architecture Overview, 🔟 Key Outcomes)
    else if (/^(?:[0-9]\ufe0f?\u20e3|\ud83d\udd1f|🔟|1\ufe0f\u20e31\ufe0f\u20e3)+\s*(.*)/.test(trimmed)) {
      const match = trimmed.match(/^(?:[0-9]\ufe0f?\u20e3|\ud83d\udd1f|🔟|1\ufe0f\u20e31\ufe0f\u20e3)+\s*(.*)/);
      const headingText = match[1].trim();
      const emojiPrefix = trimmed.substring(0, trimmed.indexOf(headingText)).trim();
      blocks.push({ type: 'emoji-heading', emoji: emojiPrefix, text: cleanAllBulletPrefixes(headingText) });
    }
    // 3. Known text headings or section breaks
    else if (
      trimmed === 'Architecture Overview' || 
      trimmed === 'Terraform Folder Structure' ||
      trimmed === 'Remote Backend Configuration' ||
      trimmed === 'Key Outcomes' ||
      trimmed === 'Challenges & Solutions' ||
      trimmed === 'Automation Benefits' ||
      trimmed === 'Security Controls Implemented'
    ) {
      blocks.push({ type: 'h2', text: trimmed });
    }
    // 4. Bullet lists
    else if (
      trimmed.startsWith('- ') || 
      trimmed.startsWith('* ') || 
      trimmed.startsWith('• ') || 
      trimmed.startsWith('▪ ') || 
      trimmed.startsWith('🔹 ') ||
      trimmed.startsWith('🚀 ') ||
      trimmed.startsWith('☸️ ') ||
      trimmed.startsWith('🐳 ') ||
      trimmed.startsWith('⚙️ ') ||
      trimmed.startsWith('📦 ') ||
      trimmed.startsWith('📊 ') ||
      trimmed.startsWith('🔒 ') ||
      trimmed.startsWith('🏆 ') ||
      trimmed.startsWith('📌 ') ||
      trimmed.startsWith('🎯 ') ||
      trimmed.startsWith('✔️ ') ||
      trimmed.startsWith('✅ ') ||
      trimmed.startsWith('👉 ')
    ) {
      const parsed = parseBulletLine(trimmed);
      blocks.push({ type: 'bullet', text: parsed.text, iconType: parsed.iconType });
    }
    // 5. Numbered lists
    else if (/^\d+\.\s/.test(trimmed)) {
      const match = trimmed.match(/^(\d+)\.\s(.*)/);
      blocks.push({ type: 'number', num: match[1], text: cleanAllBulletPrefixes(match[2]) });
    }
    // 6. Normal paragraph or fallback to bullet if it starts with an emoji
    else {
      const bulletEmojis = ['🔹', '🚀', '☸️', '🐳', '⚙️', '📦', '📊', '🔒', '🏆', '📌', '🎯', '✔️', '✅', '👉'];
      const startsWithBulletEmoji = bulletEmojis.some(emoji => trimmed.startsWith(emoji));
      if (startsWithBulletEmoji) {
        const parsed = parseBulletLine(trimmed);
        blocks.push({ type: 'bullet', text: parsed.text, iconType: parsed.iconType });
      } else {
        blocks.push({ type: 'paragraph', text: line });
      }
    }
  }
  return blocks;
};

// Extract distinct sections from summary and details fields (resolves data inconsistencies)
const extractProjectSections = (project) => {
  const summaryText = project.summary || '';
  const detailsText = project.details || '';
  
  let summary = [];
  let objective = [];
  let responsibilities = [];
  let details = [];

  const getLines = (text) => text.split('\n').map(l => l.trim());

  // 1. Parse Summary field (extract Summary, Objective, and Responsibilities if present)
  const summaryLines = getLines(summaryText);
  let currentSection = 'summary';

  for (const line of summaryLines) {
    if (line === '') continue;
    
    const cleanLine = line.toLowerCase();
    // Section match rules
    if (cleanLine.includes('summary') && (cleanLine.includes('📌') || cleanLine.includes('👉') || cleanLine.startsWith('summary'))) {
      currentSection = 'summary';
      continue;
    }
    if (cleanLine.includes('objective') && (cleanLine.includes('🎯') || cleanLine.includes('target') || cleanLine.startsWith('objective'))) {
      currentSection = 'objective';
      continue;
    }
    if (cleanLine.includes('responsibilities') && (cleanLine.includes('👨') || cleanLine.includes('key') || cleanLine.startsWith('responsibilities') || cleanLine.startsWith('key responsibilities'))) {
      currentSection = 'responsibilities';
      continue;
    }

    if (currentSection === 'summary') {
      summary.push(line);
    } else if (currentSection === 'objective') {
      objective.push(line);
    } else if (currentSection === 'responsibilities') {
      responsibilities.push(line);
    }
  }

  // 2. Parse Details field (extract Objective, Key Responsibilities, and clean Implementation Details)
  const detailsLines = detailsText.split('\n');
  currentSection = 'details'; // starts at details until a header switches it

  for (let i = 0; i < detailsLines.length; i++) {
    const line = detailsLines[i];
    const trimmed = line.trim();
    if (trimmed === '') {
      if (currentSection === 'details') {
        details.push(line);
      }
      continue;
    }

    const cleanLine = trimmed.toLowerCase();
    
    // Check for section transitions
    if (cleanLine.includes('objective') && (cleanLine.includes('🎯') || cleanLine.includes('target') || cleanLine.startsWith('objective') || cleanLine.startsWith('1. objective') || cleanLine.startsWith('1\ufe0f\u20e3 objective') || cleanLine.startsWith('1\ufe0f\u20e31\ufe0f\u20e3 objective'))) {
      currentSection = 'objective';
      continue;
    }
    if (cleanLine.includes('responsibilities') && (cleanLine.includes('👨') || cleanLine.includes('key') || cleanLine.startsWith('responsibilities') || cleanLine.startsWith('key responsibilities') || cleanLine.startsWith('2. key responsibilities') || cleanLine.startsWith('2\ufe0f\u20e3 key responsibilities'))) {
      currentSection = 'responsibilities';
      continue;
    }
    if (cleanLine.includes('implementation details') && (cleanLine.includes('📖') || cleanLine.includes('details') || cleanLine.startsWith('implementation') || cleanLine.startsWith('3. implementation') || cleanLine.startsWith('implementation details') || cleanLine.startsWith('3\ufe0f\u20e3 implementation details'))) {
      currentSection = 'details';
      continue;
    }

    if (currentSection === 'objective') {
      objective.push(trimmed);
    } else if (currentSection === 'responsibilities') {
      responsibilities.push(trimmed);
    } else {
      details.push(line); // Keep formatting intact (tabs/spaces) for code blocks
    }
  }

  // Fallback: If summary is empty but description exists, use description
  if (summary.length === 0 && project.description) {
    summary = getLines(project.description).filter(l => l !== '');
  }

  return {
    summary: summary.filter(l => l.trim() !== ''),
    objective: objective.filter(l => l.trim() !== ''),
    responsibilities: responsibilities.filter(l => l.trim() !== ''),
    details: details.join('\n')
  };
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
        
        // Decode HTML entities in fields globally to ensure proper rendering
        if (data) {
          if (data.name) data.name = data.name.replace(/&amp;/g, '&');
          if (data.title) data.title = data.title.replace(/&amp;/g, '&');
          if (data.summary) data.summary = data.summary.replace(/&amp;/g, '&');
          if (data.details) data.details = data.details.replace(/&amp;/g, '&');
          if (data.key_outcomes) data.key_outcomes = data.key_outcomes.replace(/&amp;/g, '&');
        }
        
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

  // Extract custom sections (Summary, Objective, Responsibilities, and clean Implementation Details)
  const sections = extractProjectSections(project);

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
        <h1 className="text-3xl font-bold text-foreground mb-4">{project.name}</h1>
        
        {project.image_url && (
          <img src={project.image_url} alt={project.name} className="w-full h-auto rounded-lg mb-8 shadow-md"/>
        )}

        {/* Render Project Duration if present */}
        {(project.duration || project.project_duration || project.projectDuration || project['Project Duration']) && (
          <div className="flex items-center text-sm text-muted-foreground mb-6 gap-2 bg-muted/30 w-fit px-3 py-1.5 rounded-md border border-border/50">
            <Calendar className="w-4 h-4 text-cyan-soft" />
            <span>Duration: <strong className="text-foreground">{project.duration || project.project_duration || project.projectDuration || project['Project Duration']}</strong></span>
          </div>
        )}

        {sections.summary.length > 0 && (
          <section className="mb-8">
            <h2 className="text-xl font-bold text-cyan-600 dark:text-cyan-400 mb-4 border-b border-border pb-2 flex items-center gap-2 font-sans tracking-wide">
              <Zap className="w-5 h-5 text-cyan-soft animate-pulse" />
              Summary
            </h2>
            <div className="space-y-3">
              {sections.summary.map((line, idx) => (
                <div key={idx} className="flex items-start space-x-3 text-gray-800 dark:text-gray-300 pl-1">
                  <Zap className="w-4 h-4 text-cyan-soft mt-1.5 flex-shrink-0 animate-pulse" />
                  <p className="text-base leading-relaxed font-sans">{parseBoldText(cleanAllBulletPrefixes(line))}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {sections.objective.length > 0 && (
          <section className="mb-8">
            <h2 className="text-xl font-bold text-cyan-600 dark:text-cyan-400 mb-4 border-b border-border pb-2 flex items-center gap-2 font-sans tracking-wide">
              <Sparkles className="w-5 h-5 text-cyan-soft" />
              Project Objective
            </h2>
            <div className="space-y-3">
              {sections.objective.map((line, idx) => (
                <div key={idx} className="flex items-start space-x-3 text-gray-800 dark:text-gray-300 pl-1">
                  <span className="w-2 h-2 rounded-full bg-cyan-500 dark:bg-cyan-400 mt-2.5 flex-shrink-0 shadow-[0_0_8px_rgba(6,182,212,0.6)]"></span>
                  <p className="text-base leading-relaxed font-sans">{parseBoldText(cleanAllBulletPrefixes(line))}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {sections.responsibilities.length > 0 && (
          <section className="mb-8">
            <h2 className="text-xl font-bold text-cyan-600 dark:text-cyan-400 mb-4 border-b border-border pb-2 flex items-center gap-2 font-sans tracking-wide">
              <Shield className="w-5 h-5 text-cyan-soft" />
              Key Responsibilities
            </h2>
            <div className="space-y-3">
              {sections.responsibilities.map((line, idx) => (
                <div key={idx} className="flex items-start space-x-3 text-gray-800 dark:text-gray-300 pl-1">
                  <span className="w-2 h-2 rounded-full bg-cyan-500 dark:bg-cyan-400 mt-2.5 flex-shrink-0 shadow-[0_0_8px_rgba(6,182,212,0.6)]"></span>
                  <p className="text-base leading-relaxed font-sans">{parseBoldText(cleanAllBulletPrefixes(line))}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        <section className="mb-8">
          <h2 className="text-xl font-bold text-cyan-600 dark:text-cyan-400 mb-4 border-b border-border pb-2 flex items-center gap-2 font-sans tracking-wide">
            <Cpu className="w-5 h-5 text-cyan-soft" />
            Technologies Used
          </h2>
          <div className="flex flex-wrap gap-2">
            {(project.technologies || []).map((tech) => (<Badge key={tech} variant="outline" className="border-cyan-400/30 text-cyan-soft bg-background/50 text-sm py-1 px-3">{tech}</Badge>))}
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-bold text-cyan-600 dark:text-cyan-400 mb-4 border-b border-border pb-2 flex items-center gap-2 font-sans tracking-wide">
            <CheckCircle2 className="w-5 h-5 text-cyan-soft" />
            Key Outcomes
          </h2>
          <div className="space-y-3">
            {(project.key_outcomes || '').split('\n').filter(line => line.trim() !== '').map((line, idx) => (
              <div key={idx} className="flex items-start space-x-3 text-gray-800 dark:text-gray-300 pl-1">
                <CheckCircle className="w-4 h-4 text-green-soft mt-1.5 flex-shrink-0" />
                <p className="text-base leading-relaxed font-sans">{parseBoldText(cleanAllBulletPrefixes(line))}</p>
              </div>
            ))}
          </div>
        </section>
        
        {sections.details && sections.details.trim() !== '' && (
          <section className="mb-8">
            <h2 className="text-xl font-bold text-cyan-600 dark:text-cyan-400 mb-4 border-b border-border pb-2 flex items-center gap-2 font-sans tracking-wide">
              <Terminal className="w-5 h-5 text-cyan-soft" />
              Implementation Details
            </h2>
            <div className="space-y-4">
            {groupLines(sections.details).map((block, idx) => {
              switch (block.type) {
                case 'h1':
                  return (
                    <h1 key={idx} className="text-3xl font-extrabold text-gray-900 dark:text-white mt-12 mb-6 tracking-tight border-b-2 border-cyan-500/20 pb-3 font-sans">
                      {parseBoldText(block.text)}
                    </h1>
                  );
                case 'h2':
                  return (
                    <h2 key={idx} className="text-2xl font-bold text-cyan-600 dark:text-cyan-400 mt-10 mb-4 pb-2 border-b border-border/30 font-sans tracking-wide">
                      {parseBoldText(block.text)}
                    </h2>
                  );
                case 'h3':
                  return (
                    <h3 key={idx} className="text-xl font-bold text-pink-600 dark:text-pink-400 mt-8 mb-3 font-sans tracking-wide">
                      {parseBoldText(block.text)}
                    </h3>
                  );
                case 'emoji-heading':
                  return (
                    <div key={idx} className="flex items-center gap-3 mt-10 mb-5 pb-2 border-b border-cyan-500/20">
                      <span className="flex items-center justify-center text-xl font-bold bg-cyan-600/10 dark:bg-cyan-400/10 text-cyan-600 dark:text-cyan-400 px-3 py-1 rounded-lg border border-cyan-600/20 dark:border-cyan-400/20 shadow-sm">
                        {block.emoji}
                      </span>
                      <h2 className="text-2xl font-extrabold text-gray-900 dark:text-white font-sans tracking-wide m-0">
                        {parseBoldText(block.text)}
                      </h2>
                    </div>
                  );
                case 'bullet':
                  let iconElement = <span className="w-2 h-2 rounded-full bg-cyan-600 dark:bg-cyan-400 mt-2.5 flex-shrink-0 shadow-[0_0_8px_rgba(6,182,212,0.5)]"></span>;
                  if (block.iconType === 'success') {
                    iconElement = <CheckCircle className="w-5 h-5 text-emerald-500 dark:text-emerald-400 mt-0.5 flex-shrink-0" />;
                  } else if (block.iconType === 'warning') {
                    iconElement = <AlertCircle className="w-5 h-5 text-amber-500 dark:text-amber-400 mt-0.5 flex-shrink-0" />;
                  } else if (block.iconType === 'tech') {
                    iconElement = <Cpu className="w-5 h-5 text-indigo-500 dark:text-indigo-400 mt-0.5 flex-shrink-0" />;
                  } else if (block.iconType === 'action') {
                    iconElement = <Sparkles className="w-5 h-5 text-cyan-500 dark:text-cyan-400 mt-0.5 flex-shrink-0 animate-pulse" />;
                  } else if (block.iconType === 'bullet-cyan') {
                    iconElement = <span className="w-2 h-2 rounded-full bg-cyan-500 dark:bg-cyan-400 mt-2.5 flex-shrink-0 shadow-[0_0_8px_rgba(6,182,212,0.6)]"></span>;
                  }
                  return (
                    <div key={idx} className="flex items-start gap-3 pl-3 my-2.5">
                      {iconElement}
                      <p className="text-base leading-relaxed text-gray-800 dark:text-gray-300 font-sans">
                        {parseBoldText(block.text)}
                      </p>
                    </div>
                  );
                case 'number':
                  return (
                    <div key={idx} className="flex items-start gap-3 pl-3 my-3">
                      <span className="flex items-center justify-center text-xs font-bold text-cyan-600 dark:text-cyan-400 bg-cyan-600/10 dark:bg-cyan-400/10 border border-cyan-600/20 dark:border-cyan-400/20 w-6 h-6 rounded-full flex-shrink-0 mt-0.5 shadow-sm">
                        {block.num}
                      </span>
                      <p className="text-base leading-relaxed text-gray-800 dark:text-gray-300 font-sans">
                        {parseBoldText(block.text)}
                      </p>
                    </div>
                  );
                case 'code':
                  return (
                    <div key={idx} className="my-5 rounded-lg border border-border bg-slate-950 p-5 font-mono text-xs text-slate-200 overflow-x-auto shadow-lg">
                      <div className="flex justify-between items-center text-[10px] text-slate-500 uppercase tracking-wider border-b border-slate-800 pb-2 mb-3">
                        <span className="flex items-center gap-1.5">
                          <Terminal className="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400" />
                          Configuration / Code Block
                        </span>
                      </div>
                      <pre className="whitespace-pre leading-relaxed">{block.lines.join('\n')}</pre>
                    </div>
                  );
                case 'paragraph':
                  return (
                    <div key={idx} className="flex items-start gap-3 pl-3 my-2.5 font-sans">
                      <span className="w-2 h-2 rounded-full bg-cyan-500 dark:bg-cyan-400 mt-2.5 flex-shrink-0 shadow-[0_0_8px_rgba(6,182,212,0.6)]"></span>
                      <p className="text-base leading-relaxed text-gray-800 dark:text-gray-300">
                        {parseBoldText(cleanAllBulletPrefixes(block.text))}
                      </p>
                    </div>
                  );
                case 'empty':
                default:
                  return <div key={idx} className="h-2"></div>;
              }
            })}
          </div>
        </section>
      )}

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
