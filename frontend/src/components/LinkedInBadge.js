import { useEffect } from 'react';
import { Card } from './ui/card';

export default function LinkedInBadge({ theme }) {
    useEffect(() => {
        // Force LinkedIn to parse the badge after component mounts
        // Small delay to ensure DOM is ready
        const timer = setTimeout(() => {
            if (window.IN && window.IN.parse) {
                window.IN.parse();
            }
        }, 500);

        return () => clearTimeout(timer);
    }, []); // Only run once on mount, not on theme change

    return (
        <Card className="p-4 neon-card w-full flex justify-center items-center overflow-visible transition-all hover:scale-[1.02]">
            <div className="linkedin-badge-wrapper">
                <div
                    className="badge-base LI-profile-badge"
                    data-locale="en_US"
                    data-size="large"
                    data-theme={theme}
                    data-type="HORIZONTAL"
                    data-vanity="althafhussainsyed"
                    data-version="v1"
                >
                    <a
                        className="badge-base__link LI-simple-link"
                        href="https://in.linkedin.com/in/althafhussainsyed?trk=profile-badge"
                    >
                        ALTHAF HUSSAIN SYED
                    </a>
                </div>
            </div>
        </Card>
    );
}
