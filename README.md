# Elixio Uninstaller 🚀

Hey there! Welcome to Elixio Uninstaller, your new best friend for keeping your Windows PC clean and tidy. 😎

## What's this all about? 🤔

Elixio Uninstaller is a cool little app I whipped up in Python. It helps you see all the stuff installed on your Windows computer and lets you kick out the apps you don't want anymore. No more digging through control panel or settings - it's all right here!

## Cool stuff it can do 🌟

- Shows you all the apps chillin' on your PC
- Let's you sort 'em however you like (by name, size, or when you installed 'em)
- Right-click to yeet any app you don't want
- Checks if there's a cooler, newer version of itself
- Has a fancy loading bar so you're not left wondering what's happening

## What you need to make it work 🛠️

- Python 3.7 or newer (cause we're not living in the stone age)
- A bunch of Python libraries:
  - tkinter (for making it look pretty)
  - customtkinter (for making it look even prettier)
  - requests (for chatting with the internet)
  - winreg (for sneaking around the Windows registry)
  - threading (for doing multiple things at once, like a boss)
  - datetime (for knowing what day it is)
  - subprocess (for running other programs)
  - shutil (for moving files around)
  - json (for reading config files)
  - os and sys (for general Python goodness)

## How to get it running 🏃‍♂️

### The "I know code" way:

1. Grab the code:
   ```
   git clone https://github.com/LupuC/elixio_uninstaller.git
   cd elixio_uninstaller
   ```

2. Install the extra stuff:
   ```
   pip install customtkinter requests
   ```

3. Fire it up:
   ```
   python main.py
   ```

### The "I just want to click things" way:

1. Head over to: https://github.com/LupuC/elixio_uninstaller/releases
2. Download the latest .exe and .json (otherwise, it won't work) files
3. Double-click and enjoy!

## What it looks like 📸

![Elixio in action](https://github.com/user-attachments/assets/4818b694-ea9d-4359-bfdd-6dd14da3524e)

## Known quirks 🐛

If you find any, let me know.

1. The uninstaller doesn't start the uninstall process on all the items that are shown (Important!)

## How it does its magic 🎩✨

It's basically a nosy little program that digs through your Windows Registry (don't worry, it's allowed) to find all the apps you've got. Then it puts on a fancy tkinter suit to show you everything in a nice window. It can even check GitHub to see if it needs to update itself - pretty smart, huh?

## Wanna help make it cooler? 🛠️

Hey, if you've got ideas to make this even more awesome, go for it! Fork the repo, make it better, and show me what you've got. I'm always up for learning new tricks!

## Legal mumbo-jumbo 📜

This project is under the MIT License - basically, do whatever you want with it, just don't blame me if something goes wrong. Check out the LICENSE file for the boring details.

## Shoutouts 🙌

- Big thanks to the customtkinter folks for making tkinter look like it's from this century
- Whoever came up with the idea of loading bars - you're the real MVP

Now go forth and uninstall with power! 💪🖥️
