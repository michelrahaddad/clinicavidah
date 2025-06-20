import { useState, useEffect } from 'react';
import { useIntersection } from '@/hooks/use-intersection';
import { imageCache } from '@/lib/image-cache';

interface OptimizedImageProps {
  src: string;
  alt: string;
  className?: string;
  width?: number;
  height?: number;
  priority?: boolean;
}

export default function OptimizedImage({ 
  src, 
  alt, 
  className = '', 
  width, 
  height, 
  priority = false 
}: OptimizedImageProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [imageSrc, setImageSrc] = useState<string>('');
  const [ref, isVisible] = useIntersection({ threshold: 0.1 });

  useEffect(() => {
    if (priority || isVisible) {
      const loadImage = async () => {
        try {
          await imageCache.preload(src);
          setImageSrc(src);
          setIsLoaded(true);
        } catch (error) {
          console.warn(`Failed to load image: ${src}`);
          // Fallback to direct src
          setImageSrc(src);
          setIsLoaded(true);
        }
      };

      loadImage();
    }
  }, [src, isVisible, priority]);

  return (
    <div ref={ref} className={`${className} overflow-hidden`}>
      {imageSrc && (
        <img
          src={imageSrc}
          alt={alt}
          width={width}
          height={height}
          loading={priority ? 'eager' : 'lazy'}
          decoding="async"
          className={`transition-opacity duration-300 ${
            isLoaded ? 'opacity-100' : 'opacity-0'
          } object-cover w-full h-full`}
          onLoad={() => setIsLoaded(true)}
          style={{
            contentVisibility: 'auto',
            containIntrinsicSize: width && height ? `${width}px ${height}px` : 'auto'
          }}
        />
      )}
      {!isLoaded && (
        <div 
          className="bg-gray-200 animate-pulse w-full h-full"
          style={{ 
            width: width || '100%', 
            height: height || '100%' 
          }}
        />
      )}
    </div>
  );
}