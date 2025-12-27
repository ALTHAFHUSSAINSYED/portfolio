import { useEffect, useState } from "react";
import { Card } from './ui/card';

const LINKEDIN_SCRIPT_URL = "https://platform.linkedin.com/badges/js/profile.js";

function loadLinkedInScript(callback) {
    if (window.IN && window.IN.Badge) {
        return callback();
    }
    const existing = document.querySelector(`script[src="${LINKEDIN_SCRIPT_URL}"]`);
    if (existing) {
        existing.addEventListener("load", callback);
    } else {
        const script = document.createElement("script");
        script.src = LINKEDIN_SCRIPT_URL;
        script.async = true;
        script.defer = true;
        script.onload = callback;
        document.body.appendChild(script);
    }
}

export default function LinkedInBadge({ theme }) {
    const [renderKey, setRenderKey] = useState(Date.now());

    useEffect(() => {
        // Force re-render on theme change to rebuild DOM
        setRenderKey(Date.now());
    }, [theme]);

    useEffect(() => {
        let timeout;

        function tryRender() {
            // Remove any preexisting badge container
            const badges = document.querySelectorAll(".LI-profile-badge");
            badges.forEach(badge => badge.remove());

            loadLinkedInScript(() => {
                // LinkedIn script exposes a global "IN" object
                if (window.IN && window.IN.parse) {
                    // Parse only this container
                    window.IN.parse();
                }
            });
        }

        // Wait up to 5 seconds for script to be ready
        const start = Date.now();
        function poll() {
            if (window.IN && window.IN.parse) {
                tryRender();
            } else if (Date.now() - start < 5000) {
                timeout = setTimeout(poll, 200);
            }
        }

        poll();
        return () => clearTimeout(timeout);
    }, [renderKey]);

    return (
        <Card className="p-4 neon-card w-full flex justify-center items-center overflow-hidden transition-all hover:scale-[1.02]">
            <div id="linkedin-badge-wrapper" key={renderKey} style={{ width: '100%', display: 'flex', justifyContent: 'center', minHeight: '240px' }}>
                <div className="badge-base LI-profile-badge"
                    data-locale="en_US"
                    data-size="medium"
                    data-theme={theme}
                    data-type="HORIZONTAL"
                    data-vanity="althafhussainsyed"
                    data-version="v1"></div>
            </div>
        </Card>
    );
}
