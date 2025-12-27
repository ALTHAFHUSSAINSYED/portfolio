import { Card } from './ui/card';

export default function LinkedInBadge({ theme }) {
    // Simple implementation: just render the badge HTML
    // LinkedIn's script (loaded in index.html) will automatically find and populate it
    // No need for complex useEffect, DOM manipulation, or manual parsing

    return (
        <Card className="p-4 neon-card w-full flex justify-center items-center overflow-hidden transition-all hover:scale-[1.02]">
            <div
                className="badge-base LI-profile-badge"
                data-locale="en_US"
                data-size="medium"
                data-theme={theme}
                data-type="HORIZONTAL"
                data-vanity="althafhussainsyed"
                data-version="v1"
                style={{ minHeight: '200px', width: '100%' }}
            />
        </Card>
    );
}
