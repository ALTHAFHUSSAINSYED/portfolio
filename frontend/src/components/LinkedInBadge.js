import { useEffect } from 'react';

export default function LinkedInBadge({ theme }) {
    useEffect(() => {
        // Trigger parse for light theme badge
        const timer = setTimeout(() => {
            if (window.IN && window.IN.parse) {
                window.IN.parse();
            }
        }, 500);

        return () => clearTimeout(timer);
    }, [theme]);

    return (
        <div
            className="badge-base LI-profile-badge"
            data-locale="en_US"
            data-size="large"
            data-theme="light"
            data-type="VERTICAL"
            data-vanity="althafhussainsyed"
            data-version="v1"
            style={{ overflow: 'hidden', width: '100%' }}
        >
            <a
                className="badge-base__link LI-simple-link"
                href="https://in.linkedin.com/in/althafhussainsyed?trk=profile-badge"
            >
                ALTHAF HUSSAIN SYED
            </a>
        </div>
    );
}
