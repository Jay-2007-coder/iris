import cv2

# BFMatcher with default params for ORB (Hamming distance)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

def match_features(desc1, desc2):
    """
    Matches two sets of ORB descriptors using BFMatcher.
    Returns the number of good matches.
    """
    # ORB descriptors can be None if no features were found
    if desc1 is None or desc2 is None or len(desc1) == 0 or len(desc2) == 0:
        return 0
        
    try:
        matches = bf.match(desc1, desc2)
        # Sort matches by distance (lower distance is better)
        matches = sorted(matches, key=lambda x: x.distance)
        
        # Consider a match "good" if its distance is below a certain threshold
        # For Hamming distance with ORB, < 50 is generally a good match.
        good_matches = [m for m in matches if m.distance < 50]
        
        return len(good_matches)
    except Exception as e:
        print(f"Error matching features: {e}")
        return 0

def calculate_match_score(stored_features, live_features):
    """
    Calculates a match score between stored features (left and right eye) 
    and live features.
    
    stored_features: tuple (left_desc, right_desc)
    live_features: tuple (left_desc, right_desc)
    
    Returns a combined score.
    """
    stored_left, stored_right = stored_features
    live_left, live_right = live_features
    
    score_left = match_features(stored_left, live_left)
    score_right = match_features(stored_right, live_right)
    
    # Return the sum of good matches across both eyes
    return score_left + score_right
