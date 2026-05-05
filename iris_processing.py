import cv2
import numpy as np

# Initialize OpenCV Haar Cascades
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Initialize ORB detector
# Lowered edgeThreshold and patchSize to detect features in small eye regions
orb = cv2.ORB_create(nfeatures=500, edgeThreshold=10, patchSize=10)

def preprocess_eye(eye_img):
    """Converts to grayscale, resizes, and equalizes histogram for better feature extraction."""
    if eye_img is None or eye_img.size == 0:
        return None
        
    # Convert to grayscale if it isn't already
    if len(eye_img.shape) == 3:
        gray = cv2.cvtColor(eye_img, cv2.COLOR_BGR2GRAY)
    else:
        gray = eye_img
        
    # Resize to a fixed size for consistency across different distances to camera
    resized = cv2.resize(gray, (150, 100))
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(resized, (5, 5), 0)
    
    # Apply histogram equalization to enhance contrast
    equalized = cv2.equalizeHist(blurred)
    
    return equalized

def extract_orb_features(preprocessed_eye):
    """Extracts ORB keypoints and descriptors from the preprocessed eye image."""
    if preprocessed_eye is None:
        return None, None
        
    keypoints, descriptors = orb.detectAndCompute(preprocessed_eye, None)
    return keypoints, descriptors

def process_frame(frame):
    """
    Main function to process a single frame using OpenCV Haar Cascades.
    Returns:
        - annotated_frame: frame with drawn bounding boxes around eyes
        - left_descriptors: ORB descriptors for the left eye
        - right_descriptors: ORB descriptors for the right eye
    """
    annotated_frame = frame.copy()
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    left_desc = None
    right_desc = None
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)
    
    for (x, y, w, h) in faces:
        # Draw face bounding box (optional, but good for UI)
        # cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Region of interest for eyes is within the face
        roi_gray = gray_frame[y:y+h, x:x+w]
        roi_color = annotated_frame[y:y+h, x:x+w]
        
        # Detect eyes
        eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=10, minSize=(30, 30))
        
        # Sort eyes by x-coordinate to distinguish left and right
        eyes = sorted(eyes, key=lambda e: e[0])
        
        if len(eyes) >= 2:
            # We assume the first two eyes are the actual eyes
            for i, (ex, ey, ew, eh) in enumerate(eyes[:2]):
                eye_img = roi_color[ey:ey+eh, ex:ex+ew]
                
                # Preprocess and extract features
                preprocessed = preprocess_eye(eye_img)
                _, desc = extract_orb_features(preprocessed)
                
                # Draw bounding box
                label = "L Eye" if i == 0 else "R Eye"
                color = (0, 255, 0)
                
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), color, 2)
                cv2.putText(roi_color, label, (ex, ey - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                
                if i == 0:
                    left_desc = desc
                else:
                    right_desc = desc
                    
        # Process only the first detected face
        break
        
    return annotated_frame, left_desc, right_desc
