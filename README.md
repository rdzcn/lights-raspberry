# Unicorn HAT LED Controller API

A Python Flask REST API for controlling the Pimoroni Unicorn HAT 8x8 RGB LED Matrix on a Raspberry Pi.

## 🎯 Overview

This backend accepts color data for an 8x8 grid via REST endpoints and displays the colors on the Unicorn HAT connected to your Raspberry Pi.

---

## 📋 Setup Guide for Raspberry Pi

### Prerequisites

- Raspberry Pi (any model with GPIO)
- Pimoroni Unicorn HAT (8x8 version)
- Raspberry Pi OS installed
- Network connection

### Step 1: Enable SPI Interface

The Unicorn HAT uses SPI to communicate with the Raspberry Pi.

```bash
sudo raspi-config
```

Navigate to: **Interface Options** → **SPI** → **Enable**

Reboot:
```bash
sudo reboot
```

### Step 2: Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv python3-dev git
```

### Step 3: Install Unicorn HAT Library

```bash
curl https://get.pimoroni.com/unicornhat | bash
```

Follow the prompts and reboot when asked.

### Step 4: Clone and Setup the Project

```bash
# Clone the repository (or copy files to Pi)
cd ~
git clone https://github.com/rdzcn/lights-raspberry.git
cd lights-raspberry

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install unicornhat in the venv
pip install unicornhat
```

### Step 5: Test the API

```bash
# Activate venv if not already active
source venv/bin/activate

# Run the server (requires sudo for GPIO access)
sudo venv/bin/python app.py
```

The server will start on `http://<raspberry-pi-ip>:5000`

Test with:
```bash
# From another terminal or machine
curl http://<raspberry-pi-ip>:5000/health
```

### Step 6: Set Up as a System Service (Auto-start on boot)

```bash
# Copy the service file
sudo cp unicorn_hat.service /etc/systemd/system/

# If your project is not in /home/pi/lights-raspberry, edit the service file:
sudo nano /etc/systemd/system/unicorn_hat.service
# Update WorkingDirectory and ExecStart paths

# Reload systemd
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable unicorn_hat.service

# Start the service now
sudo systemctl start unicorn_hat.service

# Check status
sudo systemctl status unicorn_hat.service
```

### Step 7: Configure Firewall (if enabled)

```bash
# Allow port 5000
sudo ufw allow 5000
```

---

## 🔌 API Endpoints

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "ok",
  "unicorn_available": true,
  "grid_size": {"width": 8, "height": 8}
}
```

### Update Full Grid

```
POST /grid
Content-Type: application/json

{
  "grid": [
    [{"r": 255, "g": 0, "b": 0}, {"r": 0, "g": 255, "b": 0}, ...],  // Row 0 (8 colors)
    [{"r": 0, "g": 0, "b": 255}, {"r": 255, "g": 255, "b": 0}, ...], // Row 1
    // ... 8 rows total, each with 8 colors
  ]
}
```

### Update Single Pixel

```
POST /pixel
Content-Type: application/json

{
  "x": 0,
  "y": 0,
  "color": {"r": 255, "g": 0, "b": 0}
}
```

### Clear Display

```
POST /clear
```

### Set Brightness

```
POST /brightness
Content-Type: application/json

{
  "brightness": 0.5  // Value between 0.0 and 1.0
}
```

---

## 🧪 Testing

### Local Testing (Simulation Mode)

On a non-Raspberry Pi machine, the API runs in simulation mode:

```bash
# Create and activate venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py

# In another terminal, run tests
python test_api.py
```

### Example: Send a Red Grid

```bash
# Create a test payload
curl -X POST http://localhost:5000/grid \
  -H "Content-Type: application/json" \
  -d '{
    "grid": [
      [{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0}],
      [{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0}],
      [{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0}],
      [{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0}],
      [{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0}],
      [{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0}],
      [{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0}],
      [{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0},{"r":255,"g":0,"b":0}]
    ]
  }'
```

---

## 🔧 Troubleshooting

### "Permission denied" errors
GPIO access requires root. Run with `sudo`:
```bash
sudo venv/bin/python app.py
```

### "No module named 'unicornhat'"
Install the unicornhat library in your venv:
```bash
source venv/bin/activate
pip install unicornhat
```

### LEDs not lighting up
1. Check if SPI is enabled: `ls /dev/spi*`
2. Verify HAT is seated properly on GPIO pins
3. Check power supply (the HAT needs adequate power)

### Service won't start
Check logs:
```bash
sudo journalctl -u unicorn_hat.service -f
```

---

## 📁 Project Structure

```
lights-raspberry/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── test_api.py         # API test script
├── unicorn_hat.service # Systemd service file
└── README.md           # This file
```

---

## 🌐 Frontend Integration

Your frontend should send POST requests to the `/grid` endpoint with the 8x8 color grid.

Example JavaScript:
```javascript
const grid = [];
for (let y = 0; y < 8; y++) {
  const row = [];
  for (let x = 0; x < 8; x++) {
    row.push({ r: 255, g: 0, b: 0 }); // Red
  }
  grid.push(row);
}

fetch('http://<raspberry-pi-ip>:5000/grid', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ grid })
});
```

---

## 📜 License

MIT License
