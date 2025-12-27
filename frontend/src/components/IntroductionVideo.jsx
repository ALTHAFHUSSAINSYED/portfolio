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
            className="intro-video-container mt-12 mb-8"
        >
            {isLoaded ? (
                <iframe
                    src="https://player.cloudinary.com/embed/?cloud_name=dtzaicj6s&public_id=introduction_video_aew8f4&profile=cld-default"
                    width="100%"
                    height="405"
                    style={{
                        maxWidth: '720px',
                        margin: '0 auto',
                        display: 'block',
                        borderRadius: '12px',
                        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
                    }}
                    allow="autoplay; fullscreen; encrypted-media; picture-in-picture"
                    allowFullScreen
                    frameBorder="0"
                    title="Introduction Video"
                />
            ) : (
                <div
                    style={{
                        maxWidth: '720px',
                        height: '405px',
                        margin: '0 auto',
                        background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(168, 85, 247, 0.1))',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'var(--foreground)',
                        fontSize: '18px',
                        fontWeight: '500'
                    }}
                >
                    Loading video...
                </div>
            )}
        </div>
    );
};

export default IntroductionVideo;
