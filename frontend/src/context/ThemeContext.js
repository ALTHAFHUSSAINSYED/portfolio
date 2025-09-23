import React, { createContext, useState, useEffect, useContext } from 'react';

// Create the context
const ThemeContext = createContext();

// Create a custom hook to use the theme context easily (this is a named export)
export const useTheme = () => useContext(ThemeContext);

// Create the provider component
const ThemeProvider = ({ children }) => {
  // State to hold the current theme, defaulting to 'dark' or what's in localStorage
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');

  // Effect to apply the theme class to the HTML element
  useEffect(() => {
    const root = window.document.documentElement;
    // Remove the opposite theme class and add the current one
    root.classList.remove(theme === 'dark' ? 'light' : 'dark');
    root.classList.add(theme);
    // Save the current theme to localStorage
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Function to toggle the theme
  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'dark' ? 'light' : 'dark'));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Make the ThemeProvider the default export so it can be imported easily
export default ThemeProvider;
