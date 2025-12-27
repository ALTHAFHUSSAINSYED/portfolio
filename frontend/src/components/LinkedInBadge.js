import React, { useEffect, useRef, useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import { Card } from './ui/card';

const LinkedInBadge = () => {
    const { theme } = useTheme();
    const containerRef = useRef(null);
    // Force a re-render/remount on theme change
    const badgeTheme = theme === 'dark' ? 'dark' : 'light';

    useEffect(() => {
        if (containerRef.current) {
            // Clear previous content
            containerRef.current.innerHTML = '';

            // Create the badge element structure
            const badgeDiv = document.createElement('div');
            badgeDiv.className = 'badge-base LI-profile-badge';
            badgeDiv.setAttribute('data-locale', 'en_US');
            badgeDiv.setAttribute('data-size', 'medium');
            badgeDiv.setAttribute('data-theme', badgeTheme);
            badgeDiv.setAttribute('data-type', 'HORIZONTAL');
            badgeDiv.setAttribute('data-vanity', 'althafhussainsyed');
            badgeDiv.setAttribute('data-version', 'v1');

            containerRef.current.appendChild(badgeDiv);

            // Robust parsing with retry mechanism
            const parseBadge = () => {
                if (window.LI && window.LI.Sync) {
                    window.LI.Sync.parse(containerRef.current);
                    return true;
                }
                return false;
            };

            // Try immediately
            if (!parseBadge()) {
                // If not ready, poll for it
                let retryCount = 0;
                const maxRetries = 50; // 5 seconds max
                const intervalId = setInterval(() => {
                    retryCount++;
                    if (parseBadge() || retryCount >= maxRetries) {
                        clearInterval(intervalId);
                    }
                }, 100);

                // Cleanup interval on unmount or re-effect
                return () => clearInterval(intervalId);
            }
        }
    }, [badgeTheme]);

    return (
        <Card className="p-4 neon-card w-full flex justify-center items-center overflow-hidden transition-all hover:scale-[1.02]">
            <div
                key={badgeTheme} // Forces fresh DOM node on theme change
                ref={containerRef}
                style={{ width: '100%', display: 'flex', justifyContent: 'center', minHeight: '240px' }}
            />
        </Card>
    );
};

export default LinkedInBadge;
