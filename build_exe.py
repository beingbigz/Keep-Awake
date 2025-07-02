#!/usr/bin/env python3
"""
Build script for creating executable from keep awake.py
"""

import os
import subprocess
import sys
import shutil

def clean_build_directories():
    """Clean previous build artifacts"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Remove spec files
    spec_files = [f for f in os.listdir('.') if f.endswith('.spec')]
    for spec_file in spec_files:
        print(f"Removing {spec_file}...")
        os.remove(spec_file)

def build_executable():
    """Build the executable using PyInstaller"""
    
    # Clean previous builds
    clean_build_directories()
    
    # PyInstaller command with options for a GUI application
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                    # Create a single executable file
        '--windowed',                   # Hide console window (GUI mode)
        '--name=KeepAwake',            # Name of the executable
        '--hidden-import=pystray',     # Ensure pystray is included
        '--hidden-import=PIL',         # Ensure PIL is included
        '--hidden-import=tkinter',     # Ensure tkinter is included
        'keep awake.py'                # Source file
    ]
    
    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(result.stdout)
        
        # Check if executable was created
        exe_path = os.path.join('dist', 'KeepAwake.exe')
        if os.path.exists(exe_path):
            print(f"\nExecutable created successfully: {exe_path}")
            print(f"File size: {os.path.getsize(exe_path) / (1024*1024):.1f} MB")
        else:
            print("Error: Executable not found in expected location")
            
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    
    return True

if __name__ == "__main__":
    print("Keep Awake - Executable Builder")
    print("=" * 40)
    
    # Check if source file exists
    if not os.path.exists('keep awake.py'):
        print("Error: 'keep awake.py' not found in current directory")
        sys.exit(1)
    
    # Build the executable
    success = build_executable()
    
    if success:
        print("\n" + "=" * 40)
        print("Build completed successfully!")
        print("You can find your executable in the 'dist' folder.")
        print("The executable is named 'KeepAwake.exe'")
    else:
        print("\nBuild failed. Please check the error messages above.")
        sys.exit(1)
