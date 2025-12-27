import React, { useEffect, useRef } from 'react';
import { useTheme } from '../context/ThemeContext';

const LinkedInBadge = () => {
    const { theme } = useTheme();
    const containerRef = useRef(null);

    useEffect(() => {
        if (containerRef.current) {
            containerRef.current.innerHTML = `
        <div class="badge-base LI-profile-badge"
             data-locale="en_US"
             data-size="medium"
             data-theme="${theme === 'dark' ? 'dark' : 'light'}"
             data-type="HORIZONTAL"
             data-vanity="althafhussainsyed"
             data-version="v1">
        </div>`;

            // Re-trigger LinkedIn script to parse the new badge
            if (window.LI && window.LI.Sync) {
                window.LI.Sync.parse(containerRef.current);
            }
        }
    }, [theme]);

    return (
        <div
            className="linkedin-badge-container"
            style={{
                textAlign: 'center',
                margin: '1.25rem auto',
                maxWidth: '340px'
            }}
        >
            <div id="linkedin-badge" ref={containerRef}></div>
        </div>
    );
};

export default LinkedInBadge;
