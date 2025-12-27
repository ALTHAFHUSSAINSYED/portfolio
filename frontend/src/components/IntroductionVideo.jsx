import { useEffect, useRef, useState } from 'react';

const IntroductionVideo = () => {
    const [isLoaded, setIsLoaded] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);
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

    // Custom thumbnail image with absolute URL
    const thumbnailUrl = `${window.location.origin}/video-thumbnail.png`;

    const handlePlay = () => {
        setIsPlaying(true);
    };

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
            <div style={{
                position: 'relative',
                paddingBottom: '56.25%', // 16:9 aspect ratio
                height: 0,
                overflow: 'hidden'
            }}>
                {/* Thumbnail overlay - always visible until video plays */}
                {!isPlaying && (
                    <div
                        onClick={handlePlay}
                        style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: '100%',
                            background: `url(${thumbnailUrl}) center/cover no-repeat`,
                            borderRadius: '8px',
                            cursor: 'pointer',
                            zIndex: 2,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                    >
                        <div style={{
                            width: '80px',
                            height: '80px',
                            borderRadius: '50%',
                            backgroundColor: 'rgba(0, 0, 0, 0.7)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            transition: 'transform 0.2s',
                        }}
                            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.1)'}
                            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                        >
                            <div style={{
                                width: 0,
                                height: 0,
                                borderLeft: '25px solid white',
                                borderTop: '15px solid transparent',
                                borderBottom: '15px solid transparent',
                                marginLeft: '8px'
                            }} />
                        </div>
                    </div>
                )}

                {/* Video iframe - loads when clicked */}
                {isLoaded && isPlaying && (
                    <iframe
                        src={`https://player.cloudinary.com/embed/?cloud_name=dtzaicj6s&public_id=introduction_video_aew8f4&profile=cld-default&autoplay=true`}
                        style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: '100%',
                            border: 'none',
                            overflow: 'hidden',
                            zIndex: 1
                        }}
                        allow="autoplay; fullscreen; encrypted-media; picture-in-picture"
                        allowFullScreen
                        frameBorder="0"
                        scrolling="no"
                        title="Introduction Video"
                    />
                )}
            </div>
        </div>
    );
};

export default IntroductionVideo;
