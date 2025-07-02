# Keep Awake

A cross-platform system utility that prevents your computer from going to sleep while allowing the screen to turn off based on your power settings.

## 🌟 Features

- **Cross-Platform Support**: Works on Windows and macOS
- **Smart Power Management**: Keeps system awake with optional display control
- **System Tray Integration**: Easy-to-use tray icon with comprehensive right-click menu
- **Auto-Quit Timer**: Set automatic shutdown timers from 10 seconds to 4 years
- **Startup Integration**: Automatically start with Windows (Windows only)
- **Display Control**: Toggle whether to keep display on or allow it to turn off
- **Real-time Status**: Live status updates in tray icon and menu
- **Lightweight**: Minimal resource usage
- **Portable**: Single executable file, no installation required
- **Console Fallback**: Works even without GUI components with full command interface
- **Duration Control**: Multiple timing options for automatic operation

## 🖥️ System Requirements

### Windows
- Windows 7 or later
- No additional software required

### macOS
- macOS 10.12 (Sierra) or later
- Uses built-in `caffeinate` command

## 📦 Installation

### Option 1: Use Pre-built Executable (Windows)
1. Download `KeepAwake.exe` from the releases
2. Run the executable directly - no installation needed
3. The application will appear in your system tray

### Option 2: Run from Source
```bash
# Clone or download the repository
# Install required dependencies
pip install pystray pillow

# Run the application
python "keep awake.py"
```

## 🚀 Usage

### GUI Mode (Default)
1. Launch the application
2. Look for the Keep Awake icon in your system tray
3. Right-click the tray icon to access options:
   - **System**: Toggle between keeping system awake and normal power management
   - **Display**: Toggle whether to keep display on or allow it to turn off
   - **Startup**: Enable/disable automatic startup with Windows (Windows only)
   - **Timer**: Set automatic quit timer with options from 10 seconds to 4 years
     - Unlimited time (Default)
     - Quick options: 10 seconds, 5/15/30 minutes, 1-16 hours
     - Extended options: 1-16 days, 1-8 months, 1-4 years
   - **Information**: Help and usage information
   - **Quit this software**: Exit the application and restore normal power settings

### Console Mode
If GUI components are not available, the application automatically runs in console mode with full command interface:
```bash
python "keep awake.py"
```
**Available commands:**
- `s` - Toggle system awake/sleep
- `d` - Toggle display on/off
- `r` - Toggle startup with Windows (Windows only)
- `t` - Set auto-quit timer
- `q` - Quit application
- `Ctrl+C` - Emergency stop and restore normal power management

### Timer Options
The timer feature allows you to automatically quit the software after a specified time:
- **Unlimited time (Default)**: Never automatically quit
- **Quick timers**: 10 seconds, 5/15/30 minutes, 1-16 hours
- **Extended timers**: 1-16 days, 1-8 months, 1-4 years
- **Real-time countdown**: Tray icon shows remaining time
- **Automatic cleanup**: Restores normal power management before quitting

### Duration Mode (Programmatic)
You can also use the application to keep the system awake for a specific duration:
```python
from keep_awake import keep_awake_for_duration

# Keep awake for 2 hours
keep_awake_for_duration(120)
```

## 🔧 How It Works

### Windows
- Uses the Windows API `SetThreadExecutionState` function
- Sets `ES_CONTINUOUS | ES_SYSTEM_REQUIRED` flags by default
- Optionally adds `ES_DISPLAY_REQUIRED` flag when display keep-on is enabled
- Prevents system sleep while allowing display sleep control
- Integrates with Windows startup registry for auto-start functionality

### macOS
- Utilizes the built-in `caffeinate` command
- Runs `caffeinate -s` to prevent system sleep
- Optionally runs `caffeinate -s -d` to also prevent display sleep
- Allows flexible display sleep control based on user preference

## 📋 Technical Details

### Dependencies
- **Python 3.6+** (for source version)
- **pystray**: System tray integration
- **Pillow (PIL)**: Icon generation
- **tkinter**: GUI components (usually included with Python)

### Architecture
```
keep_awake.py
├── Cross-platform detection
├── Windows API integration (ctypes)
├── macOS caffeinate integration
├── System tray interface (pystray)
├── Console fallback mode with full command interface
├── Auto-quit timer with threading
├── Windows startup registry integration
├── Real-time status updates
└── Power state management
```

## 🛡️ Safety Features

- **Automatic Cleanup**: Restores normal power management when exiting
- **Timer Safety**: Auto-quit timer ensures software doesn't run indefinitely
- **Force Exit**: Robust timer mechanism ensures reliable software termination
- **Error Handling**: Graceful fallbacks for missing dependencies
- **Interrupt Handling**: Proper cleanup on Ctrl+C in console mode
- **State Tracking**: Prevents duplicate wake states and conflicts
- **Registry Safety**: Secure Windows startup integration with error handling
- **Thread Safety**: Proper thread management for timer functionality

## 🎯 Use Cases

- **Long Downloads**: Keep system awake during large file downloads with auto-quit timer
- **Presentations**: Prevent sleep during presentations with display control options
- **Remote Access**: Maintain remote desktop connections with startup integration
- **Background Tasks**: Keep system running for scheduled tasks with flexible timing
- **Media Streaming**: Prevent interruptions during streaming with display management
- **Temporary Tasks**: Use timer feature for temporary keep-awake periods
- **Gaming/Streaming**: Extended operation with multi-day timer support
- **Development**: Keep development servers running with startup integration

## 🔄 States

### System States
- **Awake**: System stays awake, display control based on setting
- **Sleep**: Normal power management restored

### Display States
- **Display ON**: Screen stays on (prevents display sleep)
- **Display OFF**: Screen can turn off based on power settings

### Startup States (Windows only)
- **Startup ON**: Application starts automatically with Windows
- **Startup OFF**: Manual application start required

### Timer States
- **Unlimited time**: Default state, runs until manually quit
- **Active Timer**: Countdown active, shows remaining time in tray
- **Expired**: Timer reached zero, software automatically quits

### Tray Icon Status
Shows comprehensive status: "Keep Awake | [System] | Display [State] | Startup [State] | Timer [Status]"

## 🐛 Troubleshooting

### Common Issues

**Application doesn't appear in system tray:**
- Check if the application is running in console mode
- Ensure pystray and PIL are properly installed
- Try running from command line to see error messages

**System still goes to sleep:**
- Verify the application is in "AWAKE" state (check tray icon)
- Check Windows power settings for USB selective suspend
- On macOS, ensure the application has proper permissions
- Verify timer hasn't expired (check timer status in tray)

**Timer doesn't work:**
- Check timer status in tray icon title
- Verify timer is set to a duration other than "Unlimited time"
- Console mode shows timer countdown - use 't' command to check
- Timer automatically restores power management before quitting

**Startup integration fails (Windows):**
- Run application as administrator once to set registry entry
- Check Windows startup settings in Task Manager
- Verify antivirus isn't blocking registry modifications

**Build executable fails:**
- Ensure PyInstaller is installed: `pip install pyinstaller`
- Check that all dependencies are available
- Try building without `--windowed` flag for debugging

### Error Messages

**"pystray and/or PIL not available"**
```bash
pip install pystray pillow
```

**"Startup option is only available on Windows"**
- This is expected behavior on macOS and Linux systems
- Startup integration only works on Windows platform

**"Timer expired - quitting this software"**
- This is normal behavior when a timer reaches zero
- Set timer to "Unlimited time" to disable auto-quit
- Timer automatically restores normal power management

## 🏗️ Building from Source

### Build Executable (Windows)
```bash
# Install PyInstaller
pip install pyinstaller

# Build single executable
pyinstaller --onefile --windowed --name=KeepAwake "keep awake.py"

# Executable will be in dist/KeepAwake.exe
```

### Build with Dependencies
```bash
pyinstaller --onefile --windowed --name=KeepAwake \
    --hidden-import=pystray \
    --hidden-import=PIL \
    --hidden-import=tkinter \
    "keep awake.py"
```

## 📝 API Reference

### Core Functions

#### `keep_system_awake()`
Prevents the system from going to sleep while allowing the display to turn off.

**Returns:**
- Windows: Execution state result code
- macOS: Process ID of caffeinate command

#### `restore_normal_power()`
Restores normal power management behavior.

**Returns:**
- Windows: Execution state result code
- macOS: None

#### `keep_awake_for_duration(duration_minutes=60)`
Keeps system awake for a specified duration (legacy function).

**Parameters:**
- `duration_minutes` (int): Duration in minutes (default: 60)

#### `set_shutdown_timer(duration_name, duration_seconds)`
Sets an automatic quit timer for the application.

**Parameters:**
- `duration_name` (str): Human-readable duration name
- `duration_seconds` (int or None): Duration in seconds, None for unlimited

#### `get_timer_status()`
Returns current timer status as a formatted string.

**Returns:**
- String showing remaining time or "Unlimited time"

### Timer Functions

#### `get_timer_options()`
Returns dictionary of available timer options.

**Returns:**
- Dict mapping duration names to seconds (None for unlimited)

#### `cancel_shutdown_timer()`
Cancels any active auto-quit timer.

### Global Variables

- `state` (dict): Application state containing:
  - `is_awake` (bool): Current wake state
  - `display_on` (bool): Display keep-on state
  - `startup_enabled` (bool): Windows startup integration state
  - `shutdown_time` (datetime): Auto-quit timer target time
  - `caffeinate_process`: macOS caffeinate process reference
  - `tray_icon`: System tray icon reference

## 📄 License

This project is open source. Feel free to use, modify, and distribute according to your needs.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup
```bash
# Clone the repository
git clone <repository-url>

# Install development dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest

# Build executable for testing
python build_exe.py
```

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Run the application from command line to see detailed error messages
3. Create an issue in the repository with system details and error logs

---

**Note**: This application modifies system power settings. Always ensure you have proper permissions and understand the implications for your system's power management.
