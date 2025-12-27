import React from 'react';

export default function LinkedInBadge({ theme }) {
    const isDark = theme === 'dark';

    // Profile data
    const profileData = {
        name: "ALTHAF HUSSAIN SYED",
        title: "Cloud & Infrastructure Engineer | Devops Engineer |1X GCP Certified | 3x AWS Certified | 2x Azure Certified",
        company: "DXC Technology | Acharya Nagarjuna University",
        profileUrl: "https://www.linkedin.com/in/althafhussainsyed/",
        photoUrl: "/profile-pic.jpg" // We'll use the existing photo
    };

    return (
        <div
            style={{
                width: '100%',
                borderRadius: '12px',
                overflow: 'hidden',
                transform: 'scale(1.85, 1.1)',
                transformOrigin: 'left center',
                fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
            }}
        >
            {/* LinkedIn Header */}
            <div
                style={{
                    backgroundColor: isDark ? '#4a5568' : '#e8e5e1',
                    padding: '16px 20px',
                    display: 'flex',
                    alignItems: 'center'
                }}
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="90"
                    height="24"
                    viewBox="0 0 90 24"
                    fill={isDark ? '#ffffff' : '#0077b5'}
                >
                    <path d="M20.4,4H3.6C2.7,4,2,4.7,2,5.6v12.8c0,0.9,0.7,1.6,1.6,1.6h16.8c0.9,0,1.6-0.7,1.6-1.6V5.6C22,4.7,21.3,4,20.4,4z M8.9,17H6.4V9.9h2.5V17z M7.6,8.8c-0.8,0-1.4-0.6-1.4-1.4c0-0.8,0.6-1.4,1.4-1.4c0.8,0,1.4,0.6,1.4,1.4C9,8.2,8.4,8.8,7.6,8.8z M17.6,17h-2.5v-3.6c0-0.9,0-2.1-1.3-2.1c-1.3,0-1.5,1-1.5,2v3.7H9.9V9.9h2.4v1h0c0.3-0.6,1.1-1.3,2.3-1.3c2.5,0,2.9,1.6,2.9,3.7V17z" />
                </svg>
            </div>

            {/* Content Area */}
            <div
                style={{
                    backgroundColor: isDark ? '#000000' : '#ffffff',
                    padding: '24px',
                    color: isDark ? '#ffffff' : '#000000'
                }}
            >
                {/* Profile Photo */}
                <div style={{ marginBottom: '16px' }}>
                    <img
                        src={profileData.photoUrl}
                        alt={profileData.name}
                        style={{
                            width: '80px',
                            height: '80px',
                            borderRadius: '50%',
                            objectFit: 'cover',
                            border: `2px solid ${isDark ? '#4a5568' : '#e8e5e1'}`
                        }}
                    />
                </div>

                {/* Name */}
                <h3
                    style={{
                        fontSize: '18px',
                        fontWeight: '600',
                        margin: '0 0 12px 0',
                        lineHeight: '1.2',
                        letterSpacing: '0.3px'
                    }}
                >
                    {profileData.name}
                </h3>

                {/* Title */}
                <p
                    style={{
                        fontSize: '13px',
                        lineHeight: '1.4',
                        margin: '0 0 12px 0',
                        color: isDark ? '#d1d5db' : '#333333',
                        fontWeight: '400'
                    }}
                >
                    {profileData.title}
                </p>

                {/* Company/University */}
                <p
                    style={{
                        fontSize: '13px',
                        lineHeight: '1.4',
                        margin: '0 0 20px 0',
                        color: isDark ? '#d1d5db' : '#666666',
                        fontWeight: '400'
                    }}
                >
                    {profileData.company}
                </p>

                {/* View Profile Button */}
                <a
                    href={profileData.profileUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                        display: 'inline-block',
                        padding: '10px 24px',
                        border: `2px solid ${isDark ? '#ffffff' : '#0077b5'}`,
                        borderRadius: '24px',
                        color: isDark ? '#ffffff' : '#0077b5',
                        textDecoration: 'none',
                        fontSize: '14px',
                        fontWeight: '600',
                        transition: 'all 0.2s ease',
                        cursor: 'pointer'
                    }}
                    onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = isDark ? '#ffffff' : '#0077b5';
                        e.currentTarget.style.color = isDark ? '#000000' : '#ffffff';
                    }}
                    onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'transparent';
                        e.currentTarget.style.color = isDark ? '#ffffff' : '#0077b5';
                    }}
                >
                    View profile
                </a>
            </div>
        </div>
    );
}
