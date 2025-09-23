import React, { createContext, useContext, useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

// --- ThemeContext Logic (normally in src/context/ThemeContext.js) ---
const ThemeContext = createContext();
const useTheme = () => useContext(ThemeContext);
const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');
  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove(theme === 'dark' ? 'light' : 'dark');
    root.classList.add(theme);
    localStorage.setItem('theme', theme);
  }, [theme]);
  const toggleTheme = () => setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  return <ThemeContext.Provider value={{ theme, toggleTheme }}>{children}</ThemeContext.Provider>;
};

// --- Placeholder for components/Portfolio.js ---
// This is a simplified version of your portfolio page for demonstration
const Portfolio = () => {
  const { theme, toggleTheme } = useTheme();
  return (
    <div style={{ padding: '2rem', minHeight: '100vh', transition: 'background-color 0.3s, color 0.3s' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #444', paddingBottom: '1rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>My Portfolio</h1>
        <nav>
          <Link to="/projects/1" style={{ marginRight: '1rem' }}>View Project 1</Link>
          <button onClick={toggleTheme} style={{ padding: '0.5rem', borderRadius: '4px', cursor: 'pointer' }}>
            Toggle Theme (Current: {theme})
          </button>
        </nav>
      </header>
      <main style={{ paddingTop: '2rem' }}>
        <h2>Welcome!</h2>
        <p>This is the main portfolio content area. The theme switcher is now functional.</p>
      </main>
    </div>
  );
};

// --- Placeholder for components/ProjectDetailPage.js ---
// This is a simplified version for demonstration
const ProjectDetailPage = () => {
  const { theme } = useTheme();
  return (
    <div style={{ padding: '2rem', minHeight: '100vh', transition: 'background-color 0.3s, color 0.3s' }}>
      <header style={{ borderBottom: '1px solid #444', paddingBottom: '1rem' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>Project Detail Page</h1>
        <p>Current theme is: {theme}</p>
        <nav style={{ marginTop: '1rem' }}>
          <Link to="/">Back to Home</Link>
        </nav>
      </header>
      <main style={{ paddingTop: '2rem' }}>
        <p>This is where specific project details would be displayed. Notice the theme persists across pages.</p>
      </main>
    </div>
  );
};

// --- Main App Component ---
// This is the updated version for your project
function App() {
  return (
    <ThemeProvider>
      {/* This div applies theme-aware classes. You'll need to define `bg-background` and `text-foreground` in your CSS. */}
      <div className="App bg-background text-foreground transition-colors duration-300">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Portfolio />} />
            <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
          </Routes>
        </BrowserRouter>
      </div>
    </ThemeProvider>
  );
}

export default App;

