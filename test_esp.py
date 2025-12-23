"""
ESP32 Camera Test Script
Test ESP32 camera connection and apply optimal settings
"""
import sys
import time
from modules import esp_client

def test_esp_connection(ip: str):
    """Test basic ESP32 connection"""
    print(f"\n{'='*60}")
    print(f"🔍 Testing ESP32-CAM Connection: {ip}")
    print(f"{'='*60}\n")
    
    # Test 1: Get Status
    print("📊 Test 1: Getting camera status...")
    status_code, settings = esp_client.get_status(ip)
    
    if status_code == 200 and settings:
        print("✅ Connection successful!")
        print(f"\n📸 Current Settings:")
        print(f"   - Resolution: {settings.get('framesize', 'unknown')}")
        print(f"   - Quality: {settings.get('quality', 'unknown')}")
        print(f"   - Brightness: {settings.get('brightness', 'unknown')}")
        print(f"   - AWB: {'ON' if settings.get('awb') == 1 else 'OFF'}")
        print(f"   - AEC: {'ON' if settings.get('aec') == 1 else 'OFF'}")
        print(f"   - AGC: {'ON' if settings.get('agc') == 1 else 'OFF'}")
    else:
        print(f"❌ Connection failed! Status code: {status_code}")
        return False
    
    # Test 2: Send Command
    print("\n🔧 Test 2: Sending test command (brightness)...")
    current_brightness = settings.get('brightness', 0)
    status_code, response = esp_client.send_command(ip, {
        'var': 'brightness',
        'val': str(current_brightness)
    })
    
    if status_code == 200:
        print("✅ Command sent successfully!")
    else:
        print(f"❌ Command failed! Status code: {status_code}")
        return False
    
    # Test 3: Get Snapshot
    print("\n📷 Test 3: Capturing snapshot...")
    snapshot = esp_client.get_snapshot(ip, timeout=10)
    
    if snapshot:
        print(f"✅ Snapshot captured! Size: {len(snapshot)} bytes")
        
        # Save snapshot
        filename = f"test_snapshot_{int(time.time())}.jpg"
        with open(filename, 'wb') as f:
            f.write(snapshot)
        print(f"💾 Saved to: {filename}")
    else:
        print("⚠️  Snapshot capture failed (might be normal if stream is active)")
    
    return True


def apply_optimal_settings(ip: str):
    """Apply optimal settings for emotion analysis"""
    print(f"\n{'='*60}")
    print("⚙️  Applying Optimal Settings for Emotion Analysis")
    print(f"{'='*60}\n")
    
    print("This will configure the camera with:")
    print("  • Resolution: XGA (1024x768)")
    print("  • Quality: 10 (highest)")
    print("  • Auto White Balance: ON")
    print("  • Auto Exposure: ON")
    print("  • Auto Gain: ON")
    print("  • Face Detection: ON")
    print("  • ... and more\n")
    
    input("Press Enter to continue or Ctrl+C to cancel...")
    
    print("\n🚀 Applying settings...")
    success = esp_client.apply_emotion_analysis_preset(ip, timeout=10)
    
    if success:
        print("\n✅ All settings applied successfully!")
        print("\n💡 Recommendations:")
        print("  1. Wait 2-3 seconds for settings to take effect")
        print("  2. Ensure good lighting for best results")
        print("  3. Position face 50cm-2m from camera")
        print("  4. Look directly at camera")
    else:
        print("\n⚠️  Some settings may have failed")
        print("   Check camera connection and try again")
    
    return success


def main():
    """Main test function"""
    if len(sys.argv) < 2:
        print("Usage: python test_esp.py <ESP32_IP> [--apply-preset]")
        print("\nExamples:")
        print("  python test_esp.py 10.158.242.195")
        print("  python test_esp.py 10.158.242.195 --apply-preset")
        sys.exit(1)
    
    esp_ip = sys.argv[1]
    apply_preset = '--apply-preset' in sys.argv
    
    print("\n" + "="*60)
    print("🤖 ESP32-CAM Test Tool")
    print("="*60)
    print(f"Target IP: {esp_ip}")
    print(f"Mode: {'Test + Apply Preset' if apply_preset else 'Test Only'}")
    print("="*60)
    
    # Run connection test
    if not test_esp_connection(esp_ip):
        print("\n❌ Connection test failed! Please check:")
        print("  1. ESP32 is powered on")
        print("  2. ESP32 is on the same network")
        print("  3. IP address is correct")
        print("  4. Firewall is not blocking connection")
        sys.exit(1)
    
    # Apply preset if requested
    if apply_preset:
        time.sleep(1)
        if not apply_optimal_settings(esp_ip):
            sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ All tests completed successfully!")
    print("="*60)
    print("\n📖 Next Steps:")
    print("  1. Start Flask app: python main.py")
    print("  2. Open browser: http://localhost:5000")
    print("  3. Enter ESP32 IP and click 'Bağlan'")
    print("  4. Start emotion analysis")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
