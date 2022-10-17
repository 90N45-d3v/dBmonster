# dBmonster - Track WiFi devices with their signal strength in dBm
# by 90N45 - github.com/90N45-d3v

import os
from sys import platform
from itertools import count
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.animation import FuncAnimation

x_values = []
y_values = []
index = count() # x axis is count of dBm values

ax = plt.axes()
fig = plt.gcf()

### functions

def banner():
	print("\033[38;5;172m" + "\n                                                   --=-+-=--\n                                                        \\\n                                                   ---=--+--=---\n                 ( ( >*< ) )                             |\\\n     _  ____          |                      _     ---=----+----=---\n    | ||  _ \\         |                     | |          |\n  __| || |_) | _ __  /_\\   ___   _ __   ___ | |_   ___  _|__\n / _` ||  _ < | '_ `'_  | / _ \\ | '_ \\ / __||  _| / _ \\|  __|\n| (_| || |_) || | | | | || (_) || | | |\\__ \\| |_ |  __/| |\n \\__,_||____/ |_| |_| |_| \\___/ |_| |_||___/ \\__| \\___||_|" + "\033[38;5;27m" + "\nby github.com/90N45-d3v" + "\033[39m")

def interface_list(): # List detected interfaces
	if platform == "linux": # Linux
		print("\033[38;1;231m" + "\n\n  --- WiFi INTERFACES ---" + "\033[0m") # List WiFi INTERFACES
		os.system("airmon-ng")
	elif platform == "darwin": # MacOS
		print("\033[38;1;231m" + "\n\n  --- WiFi INTERFACES ---" + "\033[0m\n") # List WiFi INTERFACES
		os.system("networksetup -listallhardwareports | grep -A3 Wi-Fi | grep -A1 Device")

def set_channel(): # Change channel on your WiFi card
	if platform == "linux": # Linux
			os.popen("iwconfig " + interface + " channel " + channel)

	elif platform == "darwin": # MacOS
		os.popen("airport " + interface + " -c" + channel)

	else:
		exit()

def interface_check():
	if platform == "linux": # On linux, your WiFi card needs to be set in monitor mode by yourself
		mon_check = os.popen("iwconfig " + interface + " | grep Monitor -c").read()

		if mon_check == "0\n": # If interface isn't in monitor mode:
			print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Setting " + interface + " in monitor mode...")
			os.system("nmcli dev set " + interface + " managed no")
			os.system("ip link set " + interface + " down")
			os.system("iw " + interface + " set type monitor")
			os.system("ip link set " + interface + " up")

	if platform == "darwin": # On MacOS you only need to enable WiFi
		os.popen("airport " + interface + " -z") # Disconnect from WiFi network if connected

def root_check():
	user = os.popen("whoami") # Get current user who runs dBmonster

	if user.read() != "root\n":
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " This tool needs root privileges (try: sudo)\n")
		exit()

def graph(): # Plot figure
	fig.set_facecolor('black') # Window bg color
	ax.set_facecolor('black') # Graph bg color
	ax.spines['left'].set_color('#3f64d9') # Graph axis color (left)
	ax.spines['bottom'].set_color('#3f64d9') # Graph axis color (bottom)
	ax.tick_params(axis='x', colors='#3f64d9') # Graph x axis text color
	ax.tick_params(axis='y', colors='#3f64d9') # Graph y axis text color

def signal_transfer(dBm_signal): # Transfer dBm values to the plot figure
	x_values.append(next(index))
	if dBm_signal < 0: # If recieved dBm is normal, use it
		global dBm_fallback
		dBm_fallback = dBm_signal # Save current signal for line 50
		y_values.append(dBm_signal)
	elif 'dBm_fallback' in globals(): # If recieved dBm signal is broken, use last known dBm value (dBm_fallback)
		y_values.append(dBm_fallback)
	else: # If recieved dBm signal is broken, but there is no fallback, use -65 dBm (Can only be the first recieved signal)
		y_values.append(-60)
	plt.cla()
	plt.plot(x_values, y_values, color='#ff9900')
	plt.pause(0.003)

def mode1_recon(): # Scan for WiFi devices... On MacOS only Networks
	if platform == "linux": # Linux
		print("\n")
		os.system("airodump-ng " + interface + " --band abg") # --band for scanning 2.4 GHz and 5 GHz

	elif platform == "darwin": # MacOS
		print("\n")
		os.system("airport " + interface + " scan")

	else:
		exit()

def mode2_update(i): # Track MAC address
	if platform == "linux": # Linux
		dBm_signal = int(os.popen("tshark -i " + interface + " -c 1 -T fields -e radiotap.dbm_antsignal ether src " + device + " 2> /dev/null | cut -d , -f 2-").read())
	elif platform == "darwin": # MacOS
		dBm_signal = int(os.popen("tshark -i " + interface + " -I -c 1 -T fields -e radiotap.dbm_antsignal ether src " + device + " 2> /dev/null | cut -d , -f 2-").read())

	signal_transfer(dBm_signal)

def mode3_deauth_frames(i): # Deauthentication Frames
	if platform == "linux":
		dBm_signal = int(os.popen("tshark -i " + interface + " -c 1 -T fields -e radiotap.dbm_antsignal -f \"type mgt subtype deauth\" 2> /dev/null | cut -d , -f 2-").read())
	elif platform == "darwin":
		dBm_signal = int(os.popen("tshark -i " + interface + " -I -c 1 -T fields -e radiotap.dbm_antsignal -f \"type mgt subtype deauth\" 2> /dev/null | cut -d , -f 2-").read())

	signal_transfer(dBm_signal)

def mode3_beacon_frames(i): # Beacon Frames
	if platform == "linux":
		dBm_signal = int(os.popen("tshark -i " + interface + " -c 1 -T fields -e radiotap.dbm_antsignal -f \"type mgt subtype beacon\" 2> /dev/null | cut -d , -f 2-").read())
	elif platform == "darwin":
		dBm_signal = int(os.popen("tshark -i " + interface + " -I -c 1 -T fields -e radiotap.dbm_antsignal -f \"type mgt subtype beacon\" 2> /dev/null | cut -d , -f 2-").read())

	signal_transfer(dBm_signal)

def mode3_probe_frames(i): # Probe Request Frames
	if platform == "linux":
		dBm_signal = int(os.popen("tshark -i " + interface + " -c 1 -T fields -e radiotap.dbm_antsignal -f \"type mgt subtype probe-req\" 2> /dev/null | cut -d , -f 2-").read())
	elif platform == "darwin":
		dBm_signal = int(os.popen("tshark -i " + interface + " -I -c 1 -T fields -e radiotap.dbm_antsignal -f \"type mgt subtype probe-req\" 2> /dev/null | cut -d , -f 2-").read())

	signal_transfer(dBm_signal)

def mode3_auth_frames(i): # Authentication Frames
	if platform == "linux":
		dBm_signal = int(os.popen("tshark -i " + interface + " -c 1 -T fields -e radiotap.dbm_antsignal -f \"type mgt subtype auth\" 2> /dev/null | cut -d , -f 2-").read())
	elif platform == "darwin":
		dBm_signal = int(os.popen("tshark -i " + interface + " -I -c 1 -T fields -e radiotap.dbm_antsignal -f \"type mgt subtype auth\" 2> /dev/null | cut -d , -f 2-").read())

	signal_transfer(dBm_signal)

def mode4_file_analytics(): # Analyse PCAP files
	print("\033[38;1;231m" + "\n\n  --- Access Points (MAC Address, SSID) ---\n" + "\033[0m")
	os.system("tshark -r " + file + " -T fields -e wlan.sa -e wlan.ssid -Y \"wlan.fc.type_subtype == 8 and !(wlan.ssid == \\\"\\\")\" | awk '!seen[$0]++'") # Filter for Beacon frames from AP's

	print("\033[38;1;231m" + "\n\n  --- Stations (MAC Address, Searching for SSID) ---\n" + "\033[0m")
	os.system("tshark -r " + file + " -T fields -e wlan.sa -e wlan.ssid -Y \"wlan.fc.type_subtype == 4 and !(wlan.ssid == \\\"\\\")\" | awk '!seen[$0]++'") # Filter for Probe Request from stations

def mode5_from_file(): # Track MAC address from file
	os.system("tshark -r " + file + " -T fields -e radiotap.dbm_antsignal -Y \"wlan.sa == " + device + "\" 2> /dev/null | cut -d , -f 2- > tmp_dBmonster.txt") # Filter Signals and save them to temporary file

	with open('tmp_dBmonster.txt') as dBm_signal:
		for line in dBm_signal:
			x_values.append(next(index))
			y_values.append(int(line))

	plt.plot(x_values, y_values, color='#ff9900')

### workflow

while True:
	os.system("clear")
	banner()

	if platform == "win32": # Windows
		print("\033[48;5;9m" + "\n [?] WTF!?\n*** ONLY LINUX OR MAC ***" + "\033[39m")
		exit()

	root_check()
	interface_list()

	mode = input("\033[38;1;231m" + "\n\n  --- OPTIONS ---\n\n[1]" + "\033[0m" + "\tRecon Of Wireless Landscape\n" + "\033[38;1;231m" + "[2]" + "\033[0m" + "\tRealtime MAC Address Tracking\n" + "\033[38;1;231m" + "[3]" + "\033[0m" + "\tAdvanced 802.11 Frame Tracking\n\n" + "\033[38;1;231m" + "[4]" + "\033[0m" + "\tPCAP File Analytics\n" + "\033[38;1;231m" + "[5]" + "\033[0m" + "\tTracking From PCAP File\n\n" + "\033[38;1;231m" + "[0]" + "\033[0m" + "\tEXIT" + "\033[38;5;172m" + "\n\n  [*]" + "\033[0m" + " Choose Option: ")

	if mode == "1": # Recon
		interface = input("\033[38;5;172m" + "\n  [*]" + "\033[39m" + " Your WiFi interface: ")
		os.system("clear")
		mode1_recon()
		input("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Press the enter key to continue... (For tracking in realtime, remind the MAC Address and channel your target has!)")
		continue

	if mode == "2": # Track MAC address
		interface = input("\033[38;5;172m" + "\n  [*]" + "\033[39m" + " Your WiFi interface: ")
		device = input("\033[38;5;172m" + "  [*]" + "\033[39m" + " MAC address to track: ")
		channel = input("\033[38;5;172m" + "  [*]" + "\033[39m" + " WiFi channel from MAC address to track: ")
		interface_check()
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Setting " + interface + " to channel " + channel + "...")
		set_channel()
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Searching for " + device + " on channel " + channel + "...")
		if platform == "linux": # Linux
			os.system("tshark -i " + interface + " -c 1 ether src " + device + " 2> /dev/null > /dev/null")
			os.system("espeak \"device detected\" 2> /dev/null > /dev/null") # Play sound message if found...
		elif platform == "darwin": # MacOS
			os.system("tshark -i " + interface + " -I -c 1 ether src " + device + " 2> /dev/null > /dev/null")
			os.system("say device detected") # Play sound message if found...
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " START TRACKING...\n")
		fig.canvas.manager.set_window_title("dBmonster: " + device) # Window title
		graph()
		animation = FuncAnimation(fig, mode2_update, 2000)
		plt.show()
		print("\033[38;1;231m" + "\nGOOD BYE!\n" + "\033[0m")
		exit()

	if mode == "3": # Advanced 802.11 Frame Tracking
		os.system("clear")
		banner()
		interface_list()
		sub_mode = input("\033[38;1;231m" + "\n\n  --- Advanced 802.11 Frame Tracking ---\n\n[1]" + "\033[0m" + "\tDeauthentication Frames\n" + "\033[38;1;231m" + "[2]" + "\033[0m" + "\tAuthentication Frames\n" + "\033[38;1;231m" + "[3]" + "\033[0m" + "\tProbe Request Frames\n" + "\033[38;1;231m" + "[4]" + "\033[0m" + "\tBeacon Frames\n\n" + "\033[38;1;231m" + "[0]" + "\033[0m" + "\tRETURN" + "\033[38;5;172m" + "\n\n  [*]" + "\033[0m" + " Choose Option: ")
		if sub_mode == "0":
			continue
		interface = input("\033[38;5;172m" + "\n  [*]" + "\033[39m" + " Your WiFi interface: ")
		channel = input("\033[38;5;172m" + "  [*]" + "\033[39m" + " WiFi channel from frame activity: ")
		interface_check()
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Setting " + interface + " to channel " + channel + "...")
		set_channel()
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Searching for specific 802.11 frame on channel " + channel + "...")
		if sub_mode == "1":
			if platform == "linux":
				os.system("tshark -i " + interface + " -c 1 -f \"type mgt subtype deauth\" 2> /dev/null > /dev/null")
				os.system("espeak \"deauthentication frame detected\" 2> /dev/null > /dev/null") # Play sound message if found...
			elif platform == "darwin":
				os.system("tshark -i " + interface + " -I -c -f \"type mgt subtype deauth\" 2> /dev/null > /dev/null")
				os.system("say deauthentication frame detected") # Play sound message if found...
			print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " START TRACKING...\n")
			fig.canvas.manager.set_window_title("dBmonster: Deauthentication Frames") # Window title
			graph()
			animation = FuncAnimation(fig, mode3_deauth_frames, 2000)
			plt.show()

		elif sub_mode == "2":
			if platform == "linux":
				os.system("tshark -i " + interface + " -c 1 -f \"type mgt subtype auth\" 2> /dev/null > /dev/null")
				os.system("espeak \"authentication frame detected\" 2> /dev/null > /dev/null") # Play sound message if found...
			elif platform == "darwin":
				os.system("tshark -i " + interface + " -I -c 1 -f \"type mgt subtype auth\" 2> /dev/null > /dev/null")
				os.system("say authentication frame detected") # Play sound message if found...
			print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " START TRACKING...\n")
			fig.canvas.manager.set_window_title("dBmonster: Authentication Frames") # Window title
			graph()
			animation = FuncAnimation(fig, mode3_auth_frames, 2000)
			plt.show()

		elif sub_mode == "3":
			if platform == "linux":
				os.system("tshark -i " + interface + " -c 1 -f \"type mgt subtype probe-req\" 2> /dev/null > /dev/null")
				os.system("espeak \"probe request detected\" 2> /dev/null > /dev/null") # Play sound message if found...
			elif platform == "darwin":
				os.system("tshark -i " + interface + " -I -c 1 -f \"type mgt subtype probe-req\" 2> /dev/null > /dev/null")
				os.system("say probe request detected") # Play sound message if found...
			print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " START TRACKING...\n")
			fig.canvas.manager.set_window_title("dBmonster: Probe Request Frames") # Window title
			graph()
			animation = FuncAnimation(fig, mode3_probe_frames, 2000)
			plt.show()

		elif sub_mode == "4":
			if platform == "linux":
				os.system("tshark -i " + interface + " -c 1 -f \"type mgt subtype beacon\" 2> /dev/null > /dev/null")
				os.system("espeak \"beacon frame detected\" 2> /dev/null > /dev/null") # Play sound message if found...
			elif platform == "darwin":
				os.system("tshark -i " + interface + " -I -c 1 -f \"type mgt subtype beacon\" 2> /dev/null > /dev/null")
				os.system("say beacon frame detected") # Play sound message if found...
			print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " START TRACKING...\n")
			fig.canvas.manager.set_window_title("dBmonster: Beacon Frames") # Window title
			graph()
			animation = FuncAnimation(fig, mode3_beacon_frames, 2000)
			plt.show()
		print("\033[38;1;231m" + "\nGOOD BYE!\n" + "\033[0m")
		exit()

	if mode == "4": # PCAP File Analytics
		file = input("\033[38;5;172m" + "\n  [*]" + "\033[39m" + " Enter path to PCAP file: ")
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Analyzing file " + file + "...")
		mode4_file_analytics()
		input("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Press the enter key to continue... (For tracking from file, remind the MAC Address your target has!)")
		continue

	if mode == "5": # Track MAC address from file
		file = input("\033[38;5;172m" + "\n  [*]" + "\033[39m" + " Enter path to PCAP file: ")
		device = input("\033[38;5;172m" + "  [*]" + "\033[39m" + " MAC address to track: ")
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Searching for " + device + " in file " + file + "...")
		fig.canvas.manager.set_window_title("dBmonster: " + device) # Window title
		ax.set_xlabel('Amount of recieved packets') # Graph x axis label text
		ax.set_ylabel('Signal strength [dBm]') # Graph y axis label text
		ax.xaxis.label.set_color('#3f64d9') # Graph x axis label color
		ax.yaxis.label.set_color('#3f64d9') # Graph y axis label color
		graph()
		mode5_from_file()
		plt.show()
		if os.path.exists("tmp_dBmonster.txt"): # If it exists, delete temporary file
			os.remove("tmp_dBmonster.txt")
		continue

	if mode == "0": # EXIT
		if os.path.exists("tmp_dBmonster.txt"): # If it exists, delete temporary file
			os.remove("tmp_dBmonster.txt")

		print("\033[38;1;231m" + "\nGOOD BYE!\n" + "\033[0m")
		exit()
