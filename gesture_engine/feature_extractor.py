import numpy as np
from scipy import interpolate

class FeatureExtractor:
    def __init__(self, num_points=64):
        self.num_points = num_points

    def normalize(self, points):
        """Normalize points to origin and scale to unit range."""
        if len(points) < 2:
            return np.zeros((self.num_points, 2))
            
        points = np.array(points)
        
        # Translate to origin
        centroid = np.mean(points, axis=0)
        points = points - centroid
        
        # Scale to unit range
        max_dim = np.max(np.abs(points))
        if max_dim > 0:
            points = points / max_dim
            
        return points

    def resample(self, points):
        """Resample points to a fixed number of points."""
        if len(points) < 2:
            return np.zeros((self.num_points, 2))
            
        points = np.array(points)
        
        # Remove duplicate points to avoid zero-distance segments in interpolation
        mask = np.ones(len(points), dtype=bool)
        mask[1:] = np.any(np.diff(points, axis=0) != 0, axis=1)
        points = points[mask]
        
        if len(points) < 2:
            return np.tile(points[0], (self.num_points, 1)) if len(points) > 0 else np.zeros((self.num_points, 2))

        # Calculate cumulative distance
        dist = np.sqrt(np.sum(np.diff(points, axis=0)**2, axis=1))
        cumulative_dist = np.concatenate(([0], np.cumsum(dist)))
        
        if cumulative_dist[-1] == 0:
            return np.tile(points[0], (self.num_points, 1))
            
        # Interpolate
        f = interpolate.interp1d(cumulative_dist, points, axis=0, kind='linear', assume_sorted=True)
        new_dist = np.linspace(0, cumulative_dist[-1], self.num_points)
        return f(new_dist)

    def extract_features(self, points):
        """Extract flattened feature vector."""
        if len(points) < 5: # Minimum points for a gesture
            return None
            
        resampled = self.resample(points)
        normalized = self.normalize(resampled)
        
        # Direction vectors
        directions = np.diff(normalized, axis=0)
        
        # Extra features
        path_length = np.sum(np.sqrt(np.sum(np.diff(np.array(points), axis=0)**2, axis=1)))
        
        bbox_min = np.min(normalized, axis=0)
        bbox_max = np.max(normalized, axis=0)
        bbox_size = bbox_max - bbox_min
        aspect_ratio = bbox_size[0] / (bbox_size[1] + 1e-6)
        
        # Flatten and combine
        features = directions.flatten()
        
        # Final safety check for NaNs
        if np.any(np.isnan(features)):
            return None
            
        return features
