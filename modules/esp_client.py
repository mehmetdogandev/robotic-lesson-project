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
    """Send a GET request with query parameters to the ESP and return (status_code, json_or_text).

    Example usage: send_command('10.0.0.12', {'enroll':1, 'id':'abc'})
    The ESP firmware may parse different parameter names — this helper is generic.
    """
    try:
        url = _base_url(ip) + '/cmd'
        r = requests.get(url, params=params, timeout=timeout)
        try:
            return r.status_code, r.json()
        except ValueError:
            return r.status_code, r.text
    except requests.RequestException as e:
        return 0, str(e)
