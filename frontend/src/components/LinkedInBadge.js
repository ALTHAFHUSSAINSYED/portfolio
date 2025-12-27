import { useEffect, useState } from 'react';
import { Card } from './ui/card';

export default function LinkedInBadge({ theme }) {
    const [shouldRender, setShouldRender] = useState(false);

    useEffect(() => {
        // Unmount completely on theme change
        setShouldRender(false);

        // Then remount with new theme after brief delay
        const timeout = setTimeout(() => {
            setShouldRender(true);
        }, 100);

        return () => clearTimeout(timeout);
    }, [theme]);

    return (
        <Card className="p-4 neon-card w-full flex justify-center items-center overflow-hidden transition-all hover:scale-[1.02]">
            <div className="linkedin-badge-wrapper">
                {shouldRender && (
                    <div
                        className="badge-base LI-profile-badge"
                        data-locale="en_US"
                        data-size="large"
                        data-theme={theme}
                        data-type="HORIZONTAL"
                        data-vanity="althafhussainsyed"
                        data-version="v1"
                    >
                        {/* Official LinkedIn badge structure with anchor tag as primary content */}
                        <a
                            className="badge-base__link LI-simple-link"
                            href="https://in.linkedin.com/in/althafhussainsyed?trk=profile-badge"
                        >
                            ALTHAF HUSSAIN SYED
                        </a>
                    </div>
                )}
            </div>
        </Card>
    );
}
