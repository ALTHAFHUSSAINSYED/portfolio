import React, { useEffect, useRef } from 'react';
import { useTheme } from '../context/ThemeContext';
import { Card } from './ui/card';

const LinkedInBadge = () => {
    const { theme } = useTheme();
    const containerRef = useRef(null);

    useEffect(() => {
        // Determine the theme to use. LinkedIn only supports 'light' and 'dark'.
        // Default to 'light' if theme is undefined or not 'dark'.
        const badgeTheme = theme === 'dark' ? 'dark' : 'light';

        if (containerRef.current) {
            // Clear previous content strictly
            containerRef.current.innerHTML = '';

            // Create the badge element
            const badgeDiv = document.createElement('div');
            badgeDiv.className = 'badge-base LI-profile-badge';
            badgeDiv.setAttribute('data-locale', 'en_US');
            badgeDiv.setAttribute('data-size', 'medium');
            badgeDiv.setAttribute('data-theme', badgeTheme);
            badgeDiv.setAttribute('data-type', 'HORIZONTAL');
            badgeDiv.setAttribute('data-vanity', 'althafhussainsyed');
            badgeDiv.setAttribute('data-version', 'v1');

            containerRef.current.appendChild(badgeDiv);

            // Force re-parsing. 
            // If window.LI doesn't exist yet, the script in index.html will handle the initial load.
            // If it DOES exist, we need to tell it to look again.
            if (window.LI && window.LI.Sync) {
                window.LI.Sync.parse(containerRef.current);
            }
        }
    }, [theme]);

    // Styling:
    // - neon-card: Reusing the existing glow effect class
    // - w-full: Full width to match parent containers (like the WhatsApp card)
    // - overflow-hidden: Keeps the glow/border contained
    return (
        <Card className="p-4 neon-card w-full flex justify-center items-center overflow-hidden transition-all hover:scale-[1.02]">
            <div
                ref={containerRef}
                style={{ width: '100%', display: 'flex', justifyContent: 'center' }}
            />
        </Card>
    );
};

export default LinkedInBadge;
