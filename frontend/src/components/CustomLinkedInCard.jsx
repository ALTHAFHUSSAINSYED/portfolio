import './CustomLinkedInCard.css';

export default function CustomLinkedInCard({ theme }) {
    const isDark = theme === 'dark';

    return (
        <div className={`linkedin-card neon-card ${isDark ? 'dark' : 'light'}`}>
            {/* HORIZONTAL HEADER - Full width at top */}
            <div className="linkedin-header">
                <span className="linkedin-logo">Linked<span>in</span></span>
            </div>

            {/* CONTENT AREA - Profile information */}
            <div className="linkedin-body">
                <img
                    src="/profile-pic.jpg"
                    alt="Althaf Hussain Syed"
                    className="linkedin-avatar"
                />

                <h3 className="linkedin-name">ALTHAF HUSSAIN SYED</h3>

                <p className="linkedin-role">
                    Cloud &amp; Infrastructure Engineer | Devops Engineer |1X GCP Certified |
                </p>

                <p className="linkedin-role">
                    3x AWS Certified | 2x Azure Certified
                </p>

                <p className="linkedin-org">
                    DXC Technology | Acharya Nagarjuna University
                </p>

                <a
                    href="https://www.linkedin.com/in/althafhussainsyed"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="linkedin-button"
                >
                    View profile
                </a>
            </div>
        </div>
    );
}
