import { useEffect, useRef, useState } from 'react';

const IntroductionVideo = () => {
    const [isLoaded, setIsLoaded] = useState(false);
    const containerRef = useRef(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting && !isLoaded) {
                        setIsLoaded(true);
                        observer.disconnect();
                    }
                });
            },
            { threshold: 0.1 }
        );

        if (containerRef.current) {
            observer.observe(containerRef.current);
        }

        return () => observer.disconnect();
    }, [isLoaded]);

    return (
        <div
            ref={containerRef}
            className="intro-video-container mt-6 mb-6"
            style={{ overflow: 'hidden', width: '100%' }}
        >
            {isLoaded ? (
                <iframe
                    src="https://player.cloudinary.com/embed/?cloud_name=dtzaicj6s&public_id=introduction_video_aew8f4&profile=cld-default"
                    width="100%"
                    height="280"
                    style={{
                        width: '100%',
                        margin: '0',
                        display: 'block',
                        borderRadius: '8px',
                        boxShadow: '0 2px 10px rgba(0, 0, 0, 0.2)',
                        border: 'none',
                        overflow: 'hidden'
                    }}
                    allow="autoplay; fullscreen; encrypted-media; picture-in-picture"
                    allowFullScreen
                    frameBorder="0"
                    scrolling="no"
                    title="Introduction Video"
                />
            ) : (
                <div
                    style={{
                        width: '100%',
                        height: '280px',
                        margin: '0',
                        background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(168, 85, 247, 0.1))',
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'var(--foreground)',
                        fontSize: '16px',
                        fontWeight: '500',
                        overflow: 'hidden'
                    }}
                >
                    Loading video...
                </div>
            )}
        </div>
    );
};

export default IntroductionVideo;
