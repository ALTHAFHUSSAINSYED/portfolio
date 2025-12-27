import { useEffect, useRef } from 'react';

export default function LinkedInBadge({ theme }) {
    const containerRef = useRef(null);

    useEffect(() => {
        if (!containerRef.current) return;

        // Clear old iframe completely
        containerRef.current.innerHTML = '';

        // Create badge container fresh
        const badge = document.createElement('div');
        badge.className = 'badge-base LI-profile-badge';
        badge.setAttribute('data-locale', 'en_US');
        badge.setAttribute('data-size', 'large');
        badge.setAttribute('data-theme', theme);
        badge.setAttribute('data-type', 'VERTICAL');
        badge.setAttribute('data-vanity', 'althafhussainsyed');
        badge.setAttribute('data-version', 'v1');

        const link = document.createElement('a');
        link.className = 'badge-base__link LI-simple-link';
        link.href = 'https://in.linkedin.com/in/althafhussainsyed?trk=profile-badge';
        link.innerText = 'ALTHAF HUSSAIN SYED';

        badge.appendChild(link);
        containerRef.current.appendChild(badge);

        // Force LinkedIn to re-parse clean DOM
        if (window.IN && window.IN.parse) {
            window.IN.parse(containerRef.current);
        }
    }, [theme]);

    return (
        <div className="linkedin-card">
            <div ref={containerRef} />
        </div>
    );
}
