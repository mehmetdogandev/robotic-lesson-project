"""
Simple ESP HTTP client helpers.

This module provides lightweight functions to fetch a single JPEG snapshot
from an ESP camera and to send simple command requests (GET) to the ESP's
HTTP command handler. The exact command names/parameters depend on the
ESP firmware (see `esp_system/app_httpd.cpp`).

Functions:
 - get_snapshot(ip) -> bytes or None
 - send_command(ip, params) -> (status_code, content or json)

"""
from typing import Optional, Tuple
import requests


def _base_url(ip: str) -> str:
    return f'http://{ip}'


def get_snapshot(ip: str, timeout: float = 5.0) -> Optional[bytes]:
    """GET a single JPEG snapshot from the ESP.

    Tries common endpoints used by ESP camera examples:
      - /capture
      - /capture.jpg
      - /jpg

    Returns the raw bytes of the JPEG on success, or None on failure.
    """
    candidates = ['/capture', '/capture.jpg', '/jpg', '/snapshot']
    for path in candidates:
        try:
            url = _base_url(ip) + path
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200 and r.headers.get('Content-Type','').lower().startswith('image'):
                return r.content
        except requests.RequestException:
            continue
    # Fallback: try root stream capture (may return multipart)
    try:
        url = _base_url(ip) + '/stream'
        r = requests.get(url, timeout=timeout, stream=True)
        if r.status_code == 200:
            # read a chunk and try to find JPEG start/end
            data = b''
            for chunk in r.iter_content(1024):
                if not chunk:
                    break
                data += chunk
                # naive JPEG start/end search
                start = data.find(b'\xff\xd8')
                end = data.find(b'\xff\xd9')
                if start != -1 and end != -1 and end > start:
                    return data[start:end+2]
    except requests.RequestException:
        pass
    return None


def send_command(ip: str, params: dict, timeout: float = 5.0) -> Tuple[int, Optional[object]]:
    """Send a GET request with query parameters to the ESP /control endpoint.

    Example usage: send_command('10.0.0.12', {'var': 'framesize', 'val': '8'})
    The ESP firmware uses /control endpoint with 'var' and 'val' parameters.
    """
    try:
        url = _base_url(ip) + '/control'
        r = requests.get(url, params=params, timeout=timeout)
        try:
            return r.status_code, r.json()
        except ValueError:
            return r.status_code, r.text
    except requests.RequestException as e:
        return 0, str(e)


def get_status(ip: str, timeout: float = 5.0) -> Tuple[int, Optional[dict]]:
    """Get current camera status and settings from ESP /status endpoint.
    
    Returns: (status_code, settings_dict)
    """
    try:
        url = _base_url(ip) + '/status'
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.status_code, r.json()
        return r.status_code, None
    except requests.RequestException as e:
        return 0, None


def apply_emotion_analysis_preset(ip: str, timeout: float = 5.0) -> bool:
    """Apply optimal camera settings for emotion analysis.
    
    Optimal settings:
    - framesize: 8 (XGA 1024x768) - Good balance for face detection
    - quality: 10 (Best JPEG quality)
    - brightness: 0 (Default, adjust based on lighting)
    - contrast: 0 (Default, good for facial features)
    - saturation: 0 (Natural colors for skin tone detection)
    - awb: 1 (Auto White Balance ON - critical for accurate face analysis)
    - awb_gain: 1 (AWB gain ON)
    - aec: 1 (Auto Exposure ON)
    - aec2: 1 (DSP-based exposure ON)
    - ae_level: 0 (Default exposure level)
    - agc: 1 (Auto Gain ON)
    - gainceiling: 2 (Moderate gain ceiling to reduce noise)
    - bpc: 1 (Black pixel correction ON)
    - wpc: 1 (White pixel correction ON)
    - raw_gma: 1 (Raw gamma ON for better dynamic range)
    - lenc: 1 (Lens correction ON)
    - hmirror: 0 (No horizontal mirror)
    - vflip: 0 (No vertical flip)
    - dcw: 1 (Downsize EN for better performance)
    - face_detect: 1 (Face detection ON)
    
    Returns: True if all settings applied successfully
    """
    settings = [
        ('framesize', 8),      # XGA 1024x768
        ('quality', 10),        # Best quality
        ('brightness', 0),      # Default brightness
        ('contrast', 0),        # Default contrast
        ('saturation', 0),      # Natural saturation
        ('awb', 1),            # Auto White Balance ON
        ('awb_gain', 1),       # AWB gain ON
        ('aec', 1),            # Auto Exposure ON
        ('aec2', 1),           # DSP exposure ON
        ('ae_level', 0),       # Default AE level
        ('agc', 1),            # Auto Gain ON
        ('gainceiling', 2),    # Moderate gain ceiling
        ('bpc', 1),            # Black pixel correction
        ('wpc', 1),            # White pixel correction
        ('raw_gma', 1),        # Raw gamma
        ('lenc', 1),           # Lens correction
        ('hmirror', 0),        # No mirror
        ('vflip', 0),          # No flip
        ('dcw', 1),            # Downsize enable
        ('face_detect', 1),    # Face detection ON
    ]
    
    success = True
    for var, val in settings:
        status, _ = send_command(ip, {'var': var, 'val': str(val)}, timeout)
        if status != 200:
            success = False
            print(f"Failed to set {var}={val}")
    
    return success
