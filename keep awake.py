import ctypes
import time
import platform
import subprocess
import sys
import os
import winreg
import threading
from datetime import datetime, timedelta
from ctypes import wintypes

try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("Warning: GUI components not available. Running in console mode only.")

# Windows API constants
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

# Global state
state = {
    'caffeinate_process': None,
    'tray_icon': None,
    'is_awake': False,
    'display_on': False,
    'startup_enabled': True,  # Default is on
    'shutdown_timer': None,
    'shutdown_time': None,
    'shutdown_thread': None
}

# UI indicators with emoji fallback
def get_indicators():
    """Return visual indicators based on console emoji support"""
    return {
        'awake': '[●]', 'sleep': '[○]', 'display_on': '[■]', 'display_off': '[□]',
        'startup_on': '[▲]', 'startup_off': '[△]',
        'arrow': ' -> ', 'app': '[APP]', 'status': '[STATUS]', 'change': '[CHG]'
    }

def safe_print(message):
    """Print with Unicode fallback"""
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode('ascii', 'replace').decode('ascii'))

def keep_system_awake():
    """Keep system awake with optional display control"""
    if state['is_awake']:
        return
    
    system = platform.system()
    icons = get_indicators()
    
    if system == "Windows":
        flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED
        if state['display_on']:
            flags |= ES_DISPLAY_REQUIRED
            
        result = ctypes.windll.kernel32.SetThreadExecutionState(flags)
        if result == 0:
            raise Exception("Failed to set execution state")
        
        display_status = icons['display_on'] if state['display_on'] else icons['display_off']
        safe_print(f"System {icons['awake']} + Display {display_status} (Windows)")
        state['is_awake'] = True
        return result
        
    elif system == "Darwin":  # macOS
        cmd = ['caffeinate', '-s'] + (['-d'] if state['display_on'] else [])
        try:
            state['caffeinate_process'] = subprocess.Popen(cmd, 
                                                         stdout=subprocess.DEVNULL, 
                                                         stderr=subprocess.DEVNULL)
            display_status = icons['display_on'] if state['display_on'] else icons['display_off']
            safe_print(f"System {icons['awake']} + Display {display_status} (macOS)")
            state['is_awake'] = True
            return state['caffeinate_process'].pid
        except FileNotFoundError:
            raise Exception("caffeinate command not found")
    else:
        raise Exception(f"Unsupported OS: {system}")

def restore_normal_power():
    """Restore normal power management"""
    if not state['is_awake']:
        return
    
    system = platform.system()
    icons = get_indicators()
    
    if system == "Windows":
        result = ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
        if result == 0:
            raise Exception("Failed to restore normal power state")
        safe_print(f"{icons['sleep']} Normal power restored (Windows)")
        
    elif system == "Darwin":
        if state['caffeinate_process'] and state['caffeinate_process'].poll() is None:
            state['caffeinate_process'].terminate()
            state['caffeinate_process'].wait()
            state['caffeinate_process'] = None
            safe_print(f"{icons['sleep']} Normal power restored (macOS)")
    
    state['is_awake'] = False

def create_tray_image():
    """Create simple tray icon"""
    image = Image.new('RGB', (64, 64), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 48, 48), fill=(255, 255, 255))
    return image

def toggle_awake(icon, item):
    """Toggle system awake/sleep"""
    icons = get_indicators()
    
    if state['is_awake']:
        restore_normal_power()
        safe_print(f"{icons['awake']}{icons['arrow']}{icons['sleep']} System SLEEP")
    else:
        keep_system_awake()
        safe_print(f"{icons['sleep']}{icons['arrow']}{icons['awake']} System AWAKE")
    
    if TRAY_AVAILABLE:
        update_tray_title(icon)
        # Update menu to reflect new state
        update_menu(icon)

def toggle_display(icon, item):
    """Toggle display on/off"""
    icons = get_indicators()
    state['display_on'] = not state['display_on']
    
    if state['is_awake']:
        restore_normal_power()
        keep_system_awake()
    
    if TRAY_AVAILABLE:
        update_tray_title(icon)
        # Update menu to reflect new state
        update_menu(icon)
    
    status = icons['display_on'] if state['display_on'] else icons['display_off']
    safe_print(f"{icons['change']} Display {status}")

def toggle_startup(icon, item):
    """Toggle startup on/off"""
    icons = get_indicators()
    
    if platform.system() != "Windows":
        safe_print("Startup option is only available on Windows")
        return
    
    state['startup_enabled'] = not state['startup_enabled']
    
    if state['startup_enabled']:
        if enable_startup():
            status = icons['startup_on']
            safe_print(f"{icons['change']} Startup {status} - Application will start with Windows")
        else:
            state['startup_enabled'] = False  # Revert on failure
            safe_print("Failed to enable startup")
    else:
        if disable_startup():
            status = icons['startup_off']
            safe_print(f"{icons['change']} Startup {status} - Application will not start with Windows")
        else:
            state['startup_enabled'] = True  # Revert on failure
            safe_print("Failed to disable startup")
    
    if TRAY_AVAILABLE:
        update_tray_title(icon)
        # Update menu to reflect new state
        update_menu(icon)

def show_info(icon, item):
    """Show information about the application"""
    # This function will be called when Information submenu items are clicked
    # Since we can't show dialogs easily, we'll print to console
    safe_print("[INFO] Information accessed from tray menu")

def update_menu(icon):
    """Update menu with current status indicators"""
    if not TRAY_AVAILABLE:
        return
    
    icons = get_indicators()
    system_status = f"{icons['awake']} AWAKE" if state['is_awake'] else f"{icons['sleep']} SLEEP"
    display_status = f"{icons['display_on']} ON" if state['display_on'] else f"{icons['display_off']} OFF"
    startup_status = f"{icons['startup_on']} ON" if state['startup_enabled'] else f"{icons['startup_off']} OFF"
    timer_status = get_timer_status()
    
    # Create timer submenu
    timer_options = get_timer_options()
    timer_menu_items = []
    for duration_name, duration_seconds in timer_options.items():
        timer_menu_items.append(create_timer_menu_item(duration_name, duration_seconds))
    
    timer_menu = pystray.Menu(*timer_menu_items)
    
    # Create information submenu
    info_menu = pystray.Menu(
        item('System Awake: Prevents computer from sleeping', show_info),
        item('System Sleep: Allows normal power management', show_info),
        item('Display ON: Keeps screen always on', show_info),
        item('Display OFF: Allows screen to turn off', show_info),
        item('Startup ON: Application starts with Windows', show_info),
        item('Startup OFF: Manual application start required', show_info),
        item('Timer: Set automatic quit time for this software', show_info),
        pystray.Menu.SEPARATOR,
        item('How to use: Click main menu items to toggle', show_info),
        item('Default: System awake, Display off, Startup on, Timer unlimited time', show_info)
    )
    
    icon.menu = pystray.Menu(
        item(f'System (current status: {system_status})', toggle_awake),
        item(f'Display (current status: {display_status})', toggle_display),
        item(f'Startup (current status: {startup_status})', toggle_startup),
        item(f'Timer (current: {timer_status})', timer_menu),
        pystray.Menu.SEPARATOR,
        item('Information', info_menu),
        pystray.Menu.SEPARATOR,
        item('Quit this software', quit_app)
    )

def update_tray_title(icon):
    """Update tray icon title"""
    if not TRAY_AVAILABLE:
        return
    
    icons = get_indicators()
    awake_status = f"{icons['awake']} AWAKE" if state['is_awake'] else f"{icons['sleep']} SLEEP"
    display_status = f"{icons['display_on']} ON" if state['display_on'] else f"{icons['display_off']} OFF"
    startup_status = f"{icons['startup_on']} ON" if state['startup_enabled'] else f"{icons['startup_off']} OFF"
    timer_status = get_timer_status()
    icon.title = f"Keep Awake | {awake_status} | Display {display_status} | Startup {startup_status} | Timer {timer_status}"

def quit_app(icon, item):
    """Quit application"""
    icons = get_indicators()
    safe_print(f"{icons['sleep']} Quitting Keep Awake software...")
    
    # Cancel any active timer
    cancel_shutdown_timer()
    
    # Restore normal power management
    restore_normal_power()
    
    # Stop tray icon
    if TRAY_AVAILABLE and icon:
        icon.stop()
    
    safe_print("Keep Awake software quit successfully")

def run_tray_app():
    """Run system tray application"""
    if not TRAY_AVAILABLE:
        return run_console_mode()
    
    # Sync startup state with registry on startup
    sync_startup_state()
    
    keep_system_awake()
    
    # Create initial menu with status indicators
    icons = get_indicators()
    system_status = f"{icons['awake']} AWAKE" if state['is_awake'] else f"{icons['sleep']} SLEEP"
    display_status = f"{icons['display_on']} ON" if state['display_on'] else f"{icons['display_off']} OFF"
    startup_status = f"{icons['startup_on']} ON" if state['startup_enabled'] else f"{icons['startup_off']} OFF"
    timer_status = get_timer_status()
    
    # Create timer submenu
    timer_options = get_timer_options()
    timer_menu_items = []
    for duration_name, duration_seconds in timer_options.items():
        timer_menu_items.append(create_timer_menu_item(duration_name, duration_seconds))
    
    timer_menu = pystray.Menu(*timer_menu_items)
    
    # Create information submenu
    info_menu = pystray.Menu(
        item('System Awake: Prevents computer from sleeping', show_info),
        item('System Sleep: Allows normal power management', show_info),
        item('Display ON: Keeps screen always on', show_info),
        item('Display OFF: Allows screen to turn off', show_info),
        item('Startup ON: Application starts with Windows', show_info),
        item('Startup OFF: Manual application start required', show_info),
        item('Timer: Set automatic quit time for this software', show_info),
        pystray.Menu.SEPARATOR,
        item('How to use: Click main menu items to toggle', show_info),
        item('Default: System awake, Display off, Startup on, Timer unlimited time', show_info)
    )
    
    menu = pystray.Menu(
        item(f'System (current status: {system_status})', toggle_awake),
        item(f'Display (current status: {display_status})', toggle_display),
        item(f'Startup (current status: {startup_status})', toggle_startup),
        item(f'Timer (current: {timer_status})', timer_menu),
        pystray.Menu.SEPARATOR,
        item('Information', info_menu),
        pystray.Menu.SEPARATOR,
        item('Quit this software', quit_app)
    )
    
    state['tray_icon'] = pystray.Icon("keep_awake", create_tray_image(), "", menu)
    update_tray_title(state['tray_icon'])
    
    safe_print(f"{icons['app']} Started in system tray. Right-click for options.")
    startup_status = icons['startup_on'] if state['startup_enabled'] else icons['startup_off']
    timer_status = get_timer_status()
    safe_print(f"{icons['status']} Default: System {icons['awake']} + Display {icons['display_off']} + Startup {startup_status} + Timer {timer_status}")
    state['tray_icon'].run()

def run_console_mode():
    """Run in console mode"""
    icons = get_indicators()
    
    # Sync startup state with registry on startup
    sync_startup_state()
    
    try:
        keep_system_awake()
        safe_print(f"{icons['awake']} System awake. Press Ctrl+C to restore normal power.")
        display_status = icons['display_on'] if state['display_on'] else icons['display_off']
        startup_status = icons['startup_on'] if state['startup_enabled'] else icons['startup_off']
        timer_status = get_timer_status()
        safe_print(f"{icons['status']} Display: {display_status}")
        safe_print(f"{icons['status']} Startup: {startup_status}")
        safe_print(f"{icons['status']} Timer: {timer_status}")
        safe_print(f"\nCommands: 'd'=toggle display, 's'=toggle system, 'r'=toggle startup, 't'=set timer, 'q'=quit")
        print("-" * 50)
        
        while True:
            try:
                cmd = input("Command: ").strip().lower()
                if cmd == 'd':
                    state['display_on'] = not state['display_on']
                    if state['is_awake']:
                        restore_normal_power()
                        keep_system_awake()
                    display_status = icons['display_on'] if state['display_on'] else icons['display_off']
                    safe_print(f"{icons['change']} Display: {display_status}")
                elif cmd == 's':
                    if state['is_awake']:
                        restore_normal_power()
                        safe_print(f"{icons['awake']}{icons['arrow']}{icons['sleep']} System SLEEP")
                    else:
                        keep_system_awake()
                        safe_print(f"{icons['sleep']}{icons['arrow']}{icons['awake']} System AWAKE")
                elif cmd == 'r':
                    if platform.system() != "Windows":
                        safe_print("Startup option is only available on Windows")
                        continue
                    
                    state['startup_enabled'] = not state['startup_enabled']
                    
                    if state['startup_enabled']:
                        if enable_startup():
                            status = icons['startup_on']
                            safe_print(f"{icons['change']} Startup {status} - Application will start with Windows")
                        else:
                            state['startup_enabled'] = False  # Revert on failure
                            safe_print("Failed to enable startup")
                    else:
                        if disable_startup():
                            status = icons['startup_off']
                            safe_print(f"{icons['change']} Startup {status} - Application will not start with Windows")
                        else:
                            state['startup_enabled'] = True  # Revert on failure
                            safe_print("Failed to disable startup")
                elif cmd == 't':
                    safe_print("\nTimer Options:")
                    timer_options = get_timer_options()
                    options_list = list(timer_options.items())
                    
                    for i, (name, _) in enumerate(options_list):
                        safe_print(f"{i + 1}. {name}")
                    
                    try:
                        choice = input("Select timer option (number): ").strip()
                        choice_idx = int(choice) - 1
                        
                        if 0 <= choice_idx < len(options_list):
                            duration_name, duration_seconds = options_list[choice_idx]
                            set_shutdown_timer(duration_name, duration_seconds)
                        else:
                            safe_print("Invalid selection")
                    except (ValueError, IndexError):
                        safe_print("Invalid input")
                elif cmd == 'q':
                    break
            except EOFError:
                break
                
    except KeyboardInterrupt:
        safe_print(f"\n{icons['sleep']} Stopping...")
    finally:
        cancel_shutdown_timer()
        restore_normal_power()
        safe_print("Done!")

def keep_awake_for_duration(minutes=60):
    """Keep system awake for specified duration"""
    try:
        keep_system_awake()
        print(f"Keeping system awake for {minutes} minutes...")
        time.sleep(minutes * 60)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        restore_normal_power()

def get_startup_registry_key():
    """Get the Windows startup registry key"""
    return winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"

def is_startup_enabled():
    """Check if the application is set to start with Windows"""
    try:
        key_handle, key_path = get_startup_registry_key()
        with winreg.OpenKey(key_handle, key_path, 0, winreg.KEY_READ) as key:
            try:
                winreg.QueryValueEx(key, "KeepAwake")
                return True
            except FileNotFoundError:
                return False
    except Exception:
        return False

def enable_startup():
    """Add application to Windows startup"""
    try:
        key_handle, key_path = get_startup_registry_key()
        with winreg.OpenKey(key_handle, key_path, 0, winreg.KEY_SET_VALUE) as key:
            # Use the current script path or executable path
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                app_path = sys.executable
            else:
                # Running as Python script
                app_path = f'"{sys.executable}" "{os.path.abspath(__file__)}"'
            
            winreg.SetValueEx(key, "KeepAwake", 0, winreg.REG_SZ, app_path)
            return True
    except Exception as e:
        safe_print(f"Error enabling startup: {e}")
        return False

def disable_startup():
    """Remove application from Windows startup"""
    try:
        key_handle, key_path = get_startup_registry_key()
        with winreg.OpenKey(key_handle, key_path, 0, winreg.KEY_SET_VALUE) as key:
            try:
                winreg.DeleteValue(key, "KeepAwake")
                return True
            except FileNotFoundError:
                return True  # Already not in startup
    except Exception as e:
        safe_print(f"Error disabling startup: {e}")
        return False

def sync_startup_state():
    """Sync the startup state with actual registry setting and set default if needed"""
    if platform.system() == "Windows":
        # Check current registry state
        current_startup_enabled = is_startup_enabled()
        
        # If this is the first run (startup not in registry) and default is True, enable it
        if not current_startup_enabled and state['startup_enabled']:
            if enable_startup():
                safe_print("Startup enabled by default on first run")
            else:
                safe_print("Warning: Failed to enable startup on first run")
        
        # Update state to match actual registry setting
        state['startup_enabled'] = is_startup_enabled()
    else:
        # For non-Windows systems, startup is not supported
        state['startup_enabled'] = False

def get_timer_options():
    """Get available timer options with their durations in seconds"""
    return {
        'Unlimited time (Default)': None,
        '10 seconds': 10,
        '5 minutes': 5 * 60,
        '15 minutes': 15 * 60,
        '30 minutes': 30 * 60,
        '1 hour': 1 * 60 * 60,
        '2 hours': 2 * 60 * 60,
        '4 hours': 4 * 60 * 60,
        '8 hours': 8 * 60 * 60,
        '16 hours': 16 * 60 * 60,
        '1 day': 1 * 24 * 60 * 60,
        '2 days': 2 * 24 * 60 * 60,
        '4 days': 4 * 24 * 60 * 60,
        '8 days': 8 * 24 * 60 * 60,
        '16 days': 16 * 24 * 60 * 60,
        '1 month': 30 * 24 * 60 * 60,
        '2 months': 60 * 24 * 60 * 60,
        '4 months': 120 * 24 * 60 * 60,
        '8 months': 240 * 24 * 60 * 60,
        '1 year': 365 * 24 * 60 * 60,
        '2 years': 730 * 24 * 60 * 60,
        '4 years': 1460 * 24 * 60 * 60
    }

def set_shutdown_timer(duration_name, duration_seconds):
    """Set a shutdown timer for the application"""
    icons = get_indicators()
    
    # Cancel existing timer
    cancel_shutdown_timer()
    
    if duration_seconds is None:
        safe_print(f"{icons['change']} Timer: Unlimited time (Never quit this software)")
        return
    
    # Calculate shutdown time
    state['shutdown_time'] = datetime.now() + timedelta(seconds=duration_seconds)
    
    # Start timer thread
    state['shutdown_thread'] = threading.Thread(target=shutdown_timer_worker, args=(duration_seconds,))
    state['shutdown_thread'].daemon = True
    state['shutdown_thread'].start()
    
    # Format time for display
    if duration_seconds < 60:
        time_str = f"{duration_seconds} seconds"
    elif duration_seconds < 3600:
        time_str = f"{duration_seconds // 60} minutes"
    elif duration_seconds < 86400:
        time_str = f"{duration_seconds // 3600} hours"
    else:
        time_str = f"{duration_seconds // 86400} days"
    
    shutdown_time_str = state['shutdown_time'].strftime("%Y-%m-%d %H:%M:%S")
    safe_print(f"{icons['change']} Timer: This software will quit in {time_str} at {shutdown_time_str}")

def cancel_shutdown_timer():
    """Cancel the current shutdown timer"""
    if state['shutdown_time'] is not None:
        # Clear the shutdown time first to signal the worker thread to stop
        state['shutdown_time'] = None
        
        # Wait a moment for the worker thread to notice and exit
        if state['shutdown_thread'] and state['shutdown_thread'].is_alive():
            try:
                state['shutdown_thread'].join(timeout=2.0)  # Wait up to 2 seconds
            except:
                pass  # Continue even if join fails
        
        # Clear the thread reference
        state['shutdown_thread'] = None
        
        icons = get_indicators()
        safe_print(f"{icons['change']} Timer cancelled")

def shutdown_timer_worker(duration_seconds):
    """Worker thread for the shutdown timer"""
    start_time = datetime.now()
    last_update = 0
    
    while True:
        # Check if timer was cancelled
        if state['shutdown_time'] is None:
            return
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # Update tray title every 10 seconds if available
        if TRAY_AVAILABLE and state['tray_icon'] and (elapsed - last_update) >= 10:
            try:
                update_tray_title(state['tray_icon'])
                last_update = elapsed
            except:
                pass  # Continue even if tray update fails
        
        if elapsed >= duration_seconds:
            # Time to shutdown - force quit the application
            icons = get_indicators()
            safe_print(f"{icons['sleep']} Timer expired - quitting this software now")
            
            # Ensure proper cleanup and quit
            try:
                # Cancel any existing timer first
                state['shutdown_time'] = None
                
                # Restore normal power management
                restore_normal_power()
                
                # Stop tray icon if available
                if TRAY_AVAILABLE and state['tray_icon']:
                    state['tray_icon'].stop()
                
                # Force exit the application
                safe_print("Software quit successfully due to timer expiration")
                os._exit(0)  # Force exit to ensure the application terminates
                
            except Exception as e:
                safe_print(f"Error during timer shutdown: {e}")
                # Force exit even if there's an error
                os._exit(0)
            
            return
        
        # Sleep for 1 second before checking again
        time.sleep(1)

def get_timer_status():
    """Get current timer status string"""
    if state['shutdown_time'] is None:
        return "Unlimited time"
    
    remaining = state['shutdown_time'] - datetime.now()
    if remaining.total_seconds() <= 0:
        return "Expired"
    
    total_seconds = int(remaining.total_seconds())
    if total_seconds < 60:
        return f"{total_seconds}s"
    elif total_seconds < 3600:
        return f"{total_seconds // 60}m"
    elif total_seconds < 86400:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        return f"{days}d {hours}h"

def create_timer_menu_item(duration_name, duration_seconds):
    """Create a timer menu item"""
    def set_timer(icon, item):
        set_shutdown_timer(duration_name, duration_seconds)
        if TRAY_AVAILABLE:
            update_tray_title(icon)
            update_menu(icon)
    
    return item(duration_name, set_timer)

def main():
    """Main function to run the Keep Awake application"""
    run_tray_app()

if __name__ == "__main__":
    main()