"""
Asynchronous video processing module
Handles video capture and AI analysis in separate threads for performance
"""
import threading
import cv2
import time
from modules.face_analysis import analyze_emotions, analyze_age
from modules.camera import camera_stream

class AsyncVideoProcessor:
    def __init__(self, source):
        self.source = source
        self.frame = None
        self.lock = threading.Lock()
        self.running = False
        self.capture_thread = None
        self.analysis_thread = None
        self.last_frame_time = 0
        
        # Analysis results
        self.latest_age = None
        self.latest_age_category = None
        
    def start(self):
        """Starts the capture and analysis threads."""
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.analysis_thread = threading.Thread(target=self._analysis_loop)
        
        # Daemon threads exit when the main program exits
        self.capture_thread.daemon = True
        self.analysis_thread.daemon = True
        
        self.capture_thread.start()
        self.analysis_thread.start()
        
    def stop(self):
        """Stops the threads."""
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=1.0)
        if self.analysis_thread:
            self.analysis_thread.join(timeout=1.0)
            
    def _capture_loop(self):
        """Continuously captures frames from the source."""
        cap = cv2.VideoCapture(self.source)
        
        # Retry connection logic
        retry_count = 0
        while self.running and not cap.isOpened():
            if retry_count > 5:
                print(f"Failed to open source: {self.source}")
                return
            time.sleep(1)
            cap = cv2.VideoCapture(self.source)
            retry_count += 1
            
        while self.running:
            ret, frame = cap.read()
            if ret:
                with self.lock:
                    self.frame = frame
            else:
                # If stream is lost, try to reconnect
                print("Stream lost, attempting to reconnect...")
                cap.release()
                time.sleep(1)
                cap = cv2.VideoCapture(self.source)
                
            # Small sleep to prevent CPU hogging
            time.sleep(0.005)
            
        cap.release()
        
    def _analysis_loop(self):
        """Continuously runs AI analysis on the latest frame."""
        while self.running:
            # Check if detection is enabled
            if not camera_stream.is_detection_enabled():
                time.sleep(0.5)
                continue
                
            frame_copy = None
            with self.lock:
                if self.frame is not None:
                    frame_copy = self.frame.copy()
            
            if frame_copy is not None:
                try:
                    # Convert to RGB for analysis
                    rgb = cv2.cvtColor(frame_copy, cv2.COLOR_BGR2RGB)
                    
                    # Run analyses (these update global state in modules.config)
                    # We run them sequentially here, but off the main UI thread
                    analyze_emotions(rgb)
                    
                    # Run age analysis (can be less frequent if needed, but here we just run it)
                    age, category = analyze_age(rgb)
                    with self.lock:
                        self.latest_age = age
                        self.latest_age_category = category
                    
                except Exception as e:
                    print(f"Async analysis error: {e}")
            
            # Adjust sleep to control load. 
            # DeepFace is heavy, so natural delay exists.
            # But we can add a small sleep to not hammer CPU if DeepFace returns fast.
            time.sleep(0.1)

    def get_frame(self):
        """Returns the latest captured frame."""
        with self.lock:
            if self.frame is None:
                return None
            return self.frame.copy()

    def get_age_info(self):
        """Returns the latest age analysis results."""
        with self.lock:
            return self.latest_age, self.latest_age_category
