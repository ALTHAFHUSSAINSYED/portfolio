// src/index.js

import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import { ThemeProvider } from "./context/ThemeContext";
// ✨ MODIFIED: Import the tools for the new router setup
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Portfolio from "./components/Portfolio";
import ProjectDetailPage from "./components/ProjectDetailPage";
import BlogDetailPage from "./components/BlogDetailPage";
// Import the smooth scroll functionality
import "./smooth-scroll";

// ✨ NEW: Define the application routes using the modern object-based approach
const router = createBrowserRouter([
  {
    path: "/",
    element: <App />, // The App component is now the main layout
    children: [
      {
  index: true, // The Portfolio component renders at the "/" path
  element: <Portfolio />,
      },
      {
        path: "/projects/:projectId", // The detail page renders at its specific path
        element: <ProjectDetailPage />,
      },
      {
        path: "/blogs/:blogId", // Blog detail page route
        element: <BlogDetailPage />,
      },
    ],
  },
]);

const rootElement = document.getElementById("root");

// Support hydration for pre-rendered content (react-snap)
if (rootElement.hasChildNodes()) {
  ReactDOM.hydrateRoot(
    rootElement,
    <React.StrictMode>
      <ThemeProvider>
        <RouterProvider router={router} />
      </ThemeProvider>
    </React.StrictMode>
  );
} else {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <ThemeProvider>
        <RouterProvider router={router} />
      </ThemeProvider>
    </React.StrictMode>
  );
}
