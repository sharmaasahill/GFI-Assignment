"""
Setup Script for Growth For Impact Assignment
Installs all required libraries and sets up the environment
"""

import subprocess
import sys
import os

def install_requirements():
    """Install all required packages"""
    print("Installing required packages...")
    
    packages = [
        'selenium==4.15.2',
        'playwright==1.40.0', 
        'requests==2.31.0',
        'pandas==2.1.3',
        'openpyxl==3.1.2',
        'beautifulsoup4==4.12.2',
        'lxml==4.9.3',
        'webdriver-manager==4.0.1'
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"{package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
    
    # Install Playwright browsers
    try:
        print("Installing Playwright browsers...")
        subprocess.check_call([sys.executable, '-m', 'playwright', 'install'])
        print("Playwright browsers installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing Playwright browsers: {e}")

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    
    directories = [
        'data',
        'scripts', 
        'logs',
        'output'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        else:
            print(f"Directory already exists: {directory}")

def main():
    """Main setup function"""
    print("Growth For Impact Assignment Setup")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Install packages
    install_requirements()
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nNext steps:")
    print("1. Make sure you have the Excel file in the 'data' folder")
    print("2. Run: python run_assignment.py")
    print("3. The script will automatically process all companies")
    print("=" * 50)

if __name__ == "__main__":
    main()
