import { useEffect, useRef } from 'react';
import { Card } from './ui/card';

export default function LinkedInBadge({ theme }) {
    const badgeRef = useRef(null);
    const containerRef = useRef(null);

    useEffect(() => {
        // When theme changes, we need to force LinkedIn to re-render the badge
        // We do this by removing the old badge content and letting the script re-parse
        if (containerRef.current) {
            // Find any injected LinkedIn content (iframes, etc.)
            const existingContent = containerRef.current.querySelectorAll('iframe, script');
            existingContent.forEach(el => el.remove());

            // Update the data-theme attribute
            if (badgeRef.current) {
                badgeRef.current.setAttribute('data-theme', theme);

                // Trigger LinkedIn to re-parse this specific element
                // Give it a moment to settle after DOM changes
                setTimeout(() => {
                    if (window.IN && window.IN.parse) {
                        window.IN.parse(containerRef.current);
                    }
                }, 100);
            }
        }
    }, [theme]);

    return (
        <Card className="p-4 neon-card w-full flex justify-center items-center overflow-hidden transition-all hover:scale-[1.02]">
            <div ref={containerRef} style={{ width: '100%', maxWidth: '600px' }}>
                <div
                    ref={badgeRef}
                    className="badge-base LI-profile-badge"
                    data-locale="en_US"
                    data-size="large"
                    data-theme={theme}
                    data-type="HORIZONTAL"
                    data-vanity="althafhussainsyed"
                    data-version="v1"
                />
            </div>
        </Card>
    );
}
