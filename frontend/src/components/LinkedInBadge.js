import { useEffect, useState, useRef } from 'react';

export default function LinkedInBadge({ theme }) {
    const [showBadge, setShowBadge] = useState(true);
    const [currentTheme, setCurrentTheme] = useState(theme);
    const containerRef = useRef(null);

    useEffect(() => {
        // When theme changes, unmount badge, change theme, then remount
        if (theme !== currentTheme) {
            setShowBadge(false);

            const timer = setTimeout(() => {
                setCurrentTheme(theme);
                setShowBadge(true);
            }, 100);

            return () => clearTimeout(timer);
        }
    }, [theme, currentTheme]);

    useEffect(() => {
        // Re-parse LinkedIn badge when it becomes visible
        if (showBadge && containerRef.current) {
            const timer = setTimeout(() => {
                if (window.IN && window.IN.parse) {
                    window.IN.parse();
                }
            }, 300);

            return () => clearTimeout(timer);
        }
    }, [showBadge, currentTheme]);

    if (!showBadge) {
        return (
            <div style={{ minHeight: '350px', transition: 'opacity 0.2s ease' }} />
        );
    }

    return (
        <div
            ref={containerRef}
            style={{
                transition: 'opacity 0.3s ease-in-out',
                opacity: 1
            }}
        >
            <div
                className="badge-base LI-profile-badge"
                data-locale="en_US"
                data-size="large"
                data-theme={currentTheme === 'dark' ? 'dark' : 'light'}
                data-type="VERTICAL"
                data-vanity="althafhussainsyed"
                data-version="v1"
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
