import { useEffect } from 'react';

export default function LinkedInBadge({ theme }) {
    useEffect(() => {
        // Only trigger parse in dark theme
        if (theme === 'dark') {
            const timer = setTimeout(() => {
                if (window.IN && window.IN.parse) {
                    window.IN.parse();
                }
            }, 500);

            return () => clearTimeout(timer);
        }
    }, [theme]);

    // Only render badge in dark theme
    if (theme !== 'dark') {
        return null;
    }

    return (
        <div
            className="badge-base LI-profile-badge"
            data-locale="en_US"
            data-size="large"
            data-theme="dark"
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
    );
}
