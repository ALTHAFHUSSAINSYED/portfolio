import './CustomLinkedInCard.css';

export default function CustomLinkedInCard({ theme }) {
    const isDark = theme === 'dark';

    return (
        <div className={`linkedin-card ${isDark ? 'dark' : 'light'}`}>
            {/* LEFT COLUMN - LinkedIn branding */}
            <div className="linkedin-left">
                <span className="linkedin-logo">Linked<span>in</span></span>
            </div>

            {/* RIGHT COLUMN - Profile content */}
            <div className="linkedin-right">
                {/* 🔹 HORIZONTAL HEADER SPACER - pushes content down */}
                <div className="linkedin-right-header"></div>

                {/* Profile image */}
                <img
                    src="/profile-pic.jpg"
                    alt="Althaf Hussain Syed"
                    className="linkedin-avatar"
                />

                {/* Text content */}
                <h3 className="linkedin-name">ALTHAF HUSSAIN SYED</h3>

                <p className="linkedin-role">
                    Cloud &amp; Infrastructure Engineer | Devops Engineer | 1X GCP
                    Certified | 3x AWS Certified | 2x Azure Certified
                </p>

                <p className="linkedin-org">
                    DXC Technology | Acharya Nagarjuna University
                </p>

                {/* Button */}
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
