# Zero Head Tracker

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

Zero Head Tracker is a free, open-source head tracking solution that converts your head movements into controller stick inputs. Use your webcam to control games and applications hands-free with natural head movements.

<p align="center">
  <img src="https://raw.githubusercontent.com/username/zero-head-tracker/main/docs/images/demo.gif" alt="Zero Head Tracker Demo" width="600">
</p>

## Features

- **Real-time Face Tracking**: Precision head orientation tracking using facial landmarks
- **Live Settings Adjustment**: Modify sensitivity, inversion, and smoothing in real-time without restarting
- **Xbox Controller Emulation**: Seamlessly maps head movements to Xbox 360 controller sticks
- **User-friendly Interface**: Simple GUI with visual feedback and real-time statistics
- **Customizable Experience**: Adjust sensitivity, smoothing, and inversion to your preference
- **Recalibration On-the-fly**: Reset your neutral position at any time
- **Performance Optimized**: Designed for low CPU usage and high framerate

## Requirements

- Windows 10 or later (required for virtual controller support)
- Python 3.8 or higher
- Webcam

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/username/zero-head-tracker.git
   cd zero-head-tracker
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Download and install the [ViGEmBus driver](https://github.com/ViGEm/ViGEmBus/releases) (required for controller emulation)

4. Run the application:
   ```
   python zero-head-tracker.py
   ```

## Quick Start

1. Launch Zero Head Tracker
2. Adjust initial settings if desired (sensitivity, axes inversion, etc.)
3. Click "Start Tracking" and follow calibration instructions
4. Look straight at the camera when prompted for calibration
5. Move your head to control the selected analog stick
6. Adjust settings in real-time as needed for optimal experience

## Settings Explained

### Basic Settings

- **Yaw Sensitivity**: Controls how responsive horizontal head movements are (left/right turning)
- **Pitch Sensitivity**: Controls how responsive vertical head movements are (looking up/down)
- **Invert Yaw/Pitch**: Reverses the direction of movement for the respective axis
- **Control Stick**: Choose whether to control the left or right analog stick

### Advanced Settings

- **Smoothing Frames**: Higher values create smoother movement but increase latency
- **Show Face Mesh**: Displays facial landmark points for visual debugging

## Usage Tips

- **Calibration Position**: Always look straight ahead during calibration
- **Lighting**: Ensure consistent, front-facing lighting for best tracking
- **Camera Position**: Position your webcam at eye level for optimal tracking
- **Adjust In-Game Sensitivity**: Lower in-game sensitivity if movements feel too extreme
- **Find Your Sweet Spot**: Start with lower sensitivity and gradually increase

## Control Example

| Head Movement | Controller Action (Default Settings) |
|---------------|-------------------------------------|
| Turn Right    | Move stick right                    |
| Turn Left     | Move stick left                     |
| Look Up       | Move stick up                       |
| Look Down     | Move stick down                     |

## Troubleshooting

- **Virtual Controller Not Working**: Ensure ViGEmBus driver is installed correctly
- **Poor Tracking**: Check lighting conditions and camera positioning
- **High Latency**: Reduce smoothing frames setting and ensure your CPU isn't overloaded
- **Too Sensitive/Not Sensitive Enough**: Adjust sensitivity settings while tracking is active
- **Unexpected Direction**: Toggle the inversion settings for the appropriate axis

## Common Use Cases

- **Racing Games**: Look left/right to steer vehicles
- **Flight Simulators**: Control aircraft orientation naturally
- **Accessibility**: Hands-free input for users with limited mobility
- **VR Enhancement**: Combine with VR for more immersive experience
- **Photography**: Control camera panning in virtual photography modes

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Face tracking powered by [MediaPipe](https://mediapipe.dev/)
- Virtual controller functionality via [vgamepad](https://github.com/yannbouteiller/vgamepad)
- Video processing using [OpenCV](https://opencv.org/)

---

Created with ❤️ by [Your Name]