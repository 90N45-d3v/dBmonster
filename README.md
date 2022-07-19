<h1 align="center">dBmonster</h1>
<p align="center">
 <img src="https://img.shields.io/badge/Made%20with-Python-blue">
 <img src="https://img.shields.io/github/license/90N45-d3v/dBmonster.svg">
 <img src="https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg">
 <br>
 <img src="https://img.shields.io/badge/-Linux-lightblue">
 <img src="https://img.shields.io/badge/-MacOS-lightgrey">
</p>

<p align="center">
 With dBmonster you are able to scan for nearby WiFi devices and track them trough the signal strength (<a href="https://en.m.wikipedia.org/wiki/DBm">dBm</a>) of their sent packets (sniffed with <a href="https://tshark.dev/setup/about/#what-is-tsharkdev">TShark</a>).
 These dBm values will be plotted to a graph with <a href="https://matplotlib.org/">matplotlib</a>.
 It can help you to identify the exact location of nearby WiFi devices (use a <a href="https://simplewifi.com/blogs/news/omni-directional-vs-antennadirectional-antenna">directional WiFi antenna</a> for the best results) or to find out how your <a href="https://www.makeuseof.com/10-diy-long-range-wi-fi-antennas-you-can-make-at-home/">self made antenna</a> works the best (<a href="https://help.ui.com/hc/en-us/articles/115012664088-UniFi-Introduction-to-Antenna-Radiation-Patterns">antenna radiation patterns</a>).
</p>

## Features on Linux and MacOS

| Feature | Linux | MacOS |
| ------- | --------- | --------- |
| Track & scan on 2.4GHz | ✅ | ✅ |
| Track & scan on 5GHz | ✅ | ✅ |
| Scanning for AP | ✅ | ✅ |
| Scanning for STA | ✅ | |
| Beep when device found | ❓ | ✅ |
| Listing WiFi interfaces | ✅ | |

## Installation
````
git clone https://github.com/90N45-d3v/dBmonster
cd dBmonster

# Install required tools (On MacOS without sudo)
sudo python requirements.py

# Start dBmonster
sudo python dBmonster.py
````

## Working on...
- Capture signal strength data for offline graphs 
- Generate graphs from normal wireshark.pcapng file
- Generate multiple graphs in one coordinate system

## Has been successfully tested  on...

| Platform 💻 | WiFi Adapter 📡 |
| ------- | --------- |
| Kali Linux | ALFA AWUS036NHA, DIY [Bi-Quad WiFi Antenna](https://www.instructables.com/Bi-Quad-WiFi-Antenna/) |
| MacOS Monterey | Internal card 802.11 a/b/g/n/ac (MBP 2019) |
###### * *should work on any MacOS or Debian based system and with every WiFi card which supports monitor-mode*

### Additional information 
- If the tracked WiFi device is out of range or doesn't send any packets, the graph stops plotting till there is new data. So don't panic ;)
- dBmonster wasn't tested on all systems... If there are any errors or something is going wrong, contact me.
- If you used dBmonster on a non-listed Platform or WiFi Adapter, please open an issue (with Platform and WiFi Adapter information) and I will add your specification to the README.md
