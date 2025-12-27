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

    // Cloudinary thumbnail URL (auto-generated from video)
    const thumbnailUrl = "https://res.cloudinary.com/dtzaicj6s/video/upload/so_0/introduction_video_aew8f4.jpg";

    return (
        <div
            ref={containerRef}
            className="intro-video-container mt-6 mb-6"
            style={{
                overflow: 'hidden',
                width: '100%',
                position: 'relative',
                borderRadius: '8px',
                backgroundColor: '#000'
            }}
        >
            {isLoaded ? (
                <div style={{
                    position: 'relative',
                    paddingBottom: '56.25%', // 16:9 aspect ratio
                    height: 0,
                    overflow: 'hidden'
                }}>
                    <iframe
                        src={`https://player.cloudinary.com/embed/?cloud_name=dtzaicj6s&public_id=introduction_video_aew8f4&profile=cld-default&poster=${encodeURIComponent(thumbnailUrl)}`}
                        style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: '100%',
                            border: 'none',
                            overflow: 'hidden'
                        }}
                        allow="autoplay; fullscreen; encrypted-media; picture-in-picture"
                        allowFullScreen
                        frameBorder="0"
                        scrolling="no"
                        title="Introduction Video"
                    />
                </div>
            ) : (
                <div
                    style={{
                        width: '100%',
                        paddingBottom: '56.25%', // 16:9 aspect ratio
                        position: 'relative',
                        background: `url(${thumbnailUrl}) center/cover no-repeat`,
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}
                >
                    <div style={{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        color: '#fff',
                        fontSize: '16px',
                        fontWeight: '500',
                        textShadow: '0 2px 4px rgba(0,0,0,0.5)'
                    }}>
                        Loading video...
                    </div>
                </div>
            )}
        </div>
    );
};

export default IntroductionVideo;
