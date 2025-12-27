import { useEffect, useRef } from 'react';

export default function LinkedInBadge({ theme }) {
    const badgeRef = useRef(null);

    useEffect(() => {
        // Re-parse LinkedIn badge whenever theme changes
        const timer = setTimeout(() => {
            if (window.IN && window.IN.parse) {
                window.IN.parse();
            }
        }, 300);

        return () => clearTimeout(timer);
    }, [theme]);

    return (
        <div
            ref={badgeRef}
            style={{
                transition: 'opacity 0.3s ease-in-out',
                opacity: 1
            }}
        >
            <div
                className="badge-base LI-profile-badge"
                data-locale="en_US"
                data-size="large"
                data-theme={theme === 'dark' ? 'dark' : 'light'}
                data-type="VERTICAL"
                data-vanity="althafhussainsyed"
                data-version="v1"
                key={theme}
                style={{ overflow: 'hidden' }}
            >
                <a
                    className="badge-base__link LI-simple-link"
                    href="https://in.linkedin.com/in/althafhussainsyed?trk=profile-badge"
                >
                    ALTHAF HUSSAIN SYED
                </a>
            </div>
        </div>
    );
}
