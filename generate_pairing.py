"""Generate Fabric Pairing Payload - Run this to get the QR code data"""
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from fabric.crypto import SharedSecret

# Generate new pairing secret
secret = SharedSecret.new()

# Load relay config
config_path = Path("config/fabric.json")
if config_path.exists():
    config = json.loads(config_path.read_text())
else:
    print("ERROR: config/fabric.json not found!")
    print("Please create it with relay_url and relay_token first.")
    sys.exit(1)

# Create pairing payload
payload = {
    "protocol": "zenith-fabric-v1",
    "device_id": config.get("device_id", "laptop"),
    "pairing_secret": secret.export(),
    "relay_url": config.get("relay_url", ""),
    "relay_token": config.get("relay_token", "")
}

# Save the secret to config
config["pairing_secret"] = secret.export()
config_path.write_text(json.dumps(config, indent=2))

# Print pairing payload
print("\n" + "="*70)
print("ZENITH PAIRING PAYLOAD")
print("="*70)
print("\nCopy this ENTIRE JSON to pair your Android device:\n")
print(json.dumps(payload, indent=2))
print("\n" + "="*70)
print("\nSECURITY WARNING: Keep this private! Anyone with this payload")
print("can pair with your ZENITH instance.")
print("="*70 + "\n")

# Save to file for convenience
payload_file = Path("pairing_payload.json")
payload_file.write_text(json.dumps(payload, indent=2))
print(f"Also saved to: {payload_file.absolute()}\n")
