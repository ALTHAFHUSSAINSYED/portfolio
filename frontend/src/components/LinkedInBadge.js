import React, { useEffect, useRef } from 'react';
import { useTheme } from '../context/ThemeContext';
import { Card } from './ui/card';

const LinkedInBadge = () => {
    const { theme } = useTheme();
    const containerRef = useRef(null);

    // Use a derived state or just the value for the key to force re-mount
    const ptheme = theme === 'dark' ? 'dark' : 'light';

    useEffect(() => {
        // Determine the theme to use. LinkedIn only supports 'light' and 'dark'.
        const badgeTheme = theme === 'dark' ? 'dark' : 'light';

        if (containerRef.current) {
            // Clear previous content strictly (though key prop change handles parent)
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
            // We wrap in a small timeout to let the DOM settle if needed, ensuring the key-remount is done.
            setTimeout(() => {
                if (window.LI && window.LI.Sync) {
                    window.LI.Sync.parse(containerRef.current);
                }
            }, 50);
        }
    }, [theme]);

    // Styling:
    // - neon-card: Reusing the existing glow effect class
    // - w-full: Full width to match parent containers
    // - key={ptheme}: CRITICAL. Forces React to destroy and recreate this DOM node when theme changes.
    //   This ensures the LinkedIn script sees a "fresh" element to parse, avoiding update glitches.
    return (
        <Card className="p-4 neon-card w-full flex justify-center items-center overflow-hidden transition-all hover:scale-[1.02]">
            <div
                key={ptheme}
                ref={containerRef}
                style={{ width: '100%', display: 'flex', justifyContent: 'center', minHeight: '200px' }}
            />
        </Card>
    );
};

export default LinkedInBadge;
