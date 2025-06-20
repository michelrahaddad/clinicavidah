// Advanced image caching system for optimal performance
class ImageCache {
  private cache = new Map<string, HTMLImageElement>();
  private preloadQueue = new Set<string>();

  preload(src: string): Promise<void> {
    if (this.cache.has(src) || this.preloadQueue.has(src)) {
      return Promise.resolve();
    }

    this.preloadQueue.add(src);

    return new Promise((resolve, reject) => {
      const img = new Image();
      
      img.onload = () => {
        this.cache.set(src, img);
        this.preloadQueue.delete(src);
        resolve();
      };
      
      img.onerror = () => {
        this.preloadQueue.delete(src);
        reject(new Error(`Failed to load image: ${src}`));
      };
      
      img.src = src;
    });
  }

  get(src: string): HTMLImageElement | null {
    return this.cache.get(src) || null;
  }

  clear(): void {
    this.cache.clear();
    this.preloadQueue.clear();
  }

  preloadCritical(images: string[]): Promise<void[]> {
    return Promise.all(images.map(src => this.preload(src)));
  }
}

export const imageCache = new ImageCache();