# 📥 Downloader v1.0 (by theking-cs)

**Downloader** is a powerful and lightweight plugin for **Enigma2** receivers (Dreambox, Vu+, Octagon, etc.). It allows you to manage multimedia downloads directly from your set-top box and play them instantly.

---

## 🚀 Quick Installation (Terminal)

Copy and paste the following command into your terminal (PuTTY, Terminal, or Linux console) to install the plugin automatically:

This plugin transforms your receiver into a smart download hub with the following capabilities:
• Integrated Web Server: Access from your mobile, tablet, or PC via port 7447 of your box to paste download links (YouTube, etc.).
• File Management: View, play, and delete songs or videos directly from the TV interface.
• Customizable Player: Choose between different playback engines (GStreamer, GstPlayer, or ExtPlayer3) to ensure maximum compatibility.
• Auto-Refresh: The file list updates automatically when entering the plugin or when deleting files via the web interface.
• Automatic Cleanup: When deleting files, the plugin also removes temporary files and playback markers (.cuts, .meta) to keep your hard drive clean.
🖥️ Web Interface Usage
Once installed, open the browser on your phone or PC and type:
http://YOUR-DEVICE-IP:7447
From there you can:
1.	Paste URLs to download audio (M4A) or Video (HD).
2.	View the list of your current downloads.
3.	Remote Delete content to free up space.
📂 Plugin Directories
• Plugin Path: /usr/lib/enigma2/python/Plugins/Extensions/downloader
• Downloads Folder: /media/hdd/Mp3 (created automatically).
• Execution Script: /usr/bin/descargador.sh
📝 Requirements
• Python 3 based image (OpenATV, OpenPLI, Egami, etc.).
• Internet connection.
• Hard Drive or USB stick mounted at /media/hdd.

wget --no-check-certificate -qO- https://raw.githubusercontent.com/theking-cs/downloader/main/install.sh | bash

Developed by theking-cs
