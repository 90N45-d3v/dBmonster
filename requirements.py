# dBmonster installer - Install required tools and libraries
# by 90N45 - github.com/90N45-d3v

import os
from sys import platform

### functions

def banner():
	print("\033[38;5;172m" + "\n                                                   --=-+-=--\n                                                        \\\n                                                   ---=--+--=---\n                 ( ( >*< ) )                             |\\\n     _  ____          |                      _     ---=----+----=---\n    | ||  _ \\         |                     | |          |\n  __| || |_) | _ __  /_\\   ___   _ __   ___ | |_   ___  _|__\n / _` ||  _ < | '_ `'_  | / _ \\ | '_ \\ / __||  _| / _ \\|  __|\n| (_| || |_) || | | | | || (_) || | | |\\__ \\| |_ |  __/| |\n \\__,_||____/ |_| |_| |_| \\___/ |_| |_||___/ \\__| \\___||_|" + "\033[38;5;27m" + "\nby github.com/90N45-d3v" + "\033[39m\n\n")

def root_check():
	user = os.popen("whoami") # Get current user who runs dBmonster

	if user.read() != "root\n":
		print("\033[38;5;206m" + " [!]" + "\033[39m" + " You need root privileges (try: sudo)\n")
		exit()

def anti_root_check():
	user = os.popen("whoami") # Get current user who runs dBmonster

	if user.read() == "root\n":
		print("\033[38;5;206m" + " [!]" + "\033[39m" + " Pleasy do not run this installer with root privileges. (Homebrew can not install tools...)\n")
		exit()

###  workflow

banner()

if platform == "darwin": # MacOS

	brew_check = os.popen("brew -v 2> /dev/null | head -n 1 | grep Homebrew -c").read() # Check if homebrew is installed

	if brew_check == "1\n":
		anti_root_check()
		print("\033[38;5;206m" + "[!]" + "\033[39m" + " Installing tshark with Homebrew...") # This don't work with sudo
		os.system("brew install wireshark") # Can only install wireshark & tshark together

	else:
		brew_install = input("\033[38;5;206m" + "[!]" + "\033[39m" + " You need to install Homebrew (Package Manager for MacOS)... Want to install it now? (may take some time) [Y/n]: ")

		if brew_install == "y" or brew_install == "Y":
			os.system("/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
			os.system("brew install wireshark") # Can only install wireshark & tshark together
		else:
			print("\033[38;5;206m" + "\n[!]" + "\033[39m" + " More information for Homebrew's installation at https://brew.sh/\n")
			exit()

if platform == "linux": # Linux
	root_check()
	print("\033[38;5;206m" + "[!]" + "\033[39m" + " Installing tshark, aircrack-ng, network-manager, wireless-tools and iproute2 with APT...")
	os.system("apt install tshark aircrack-ng network-manager wireless-tools iproute2 espeak")

print("\033[38;5;206m" + "[!]" + "\033[39m" + " Installing matplotlib from pip...")
os.system("pip install matplotlib")

print("\033[38;1;231m" + "\nInstallation completed!\n" + "\033[0m")
