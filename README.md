
<h1 align="center">
  <br>
  Maple-Bot
  <br>
</h1>

<h4 align="center">A handy Discord bot designed to make your life easier.</h4>

<p align="center">
  <a href="https://github.com/TheGreatAlphaA/Maple-bot/releases/latest" target="_blank"><img src="https://img.shields.io/badge/release-v6.4-grey?style=flat-square&color=orange"/></a>
  <a href="https://www.python.org/" target="_blank"><img src="https://img.shields.io/badge/python-3.9%2B-grey?style=flat-square&logo=python&logoColor=white&color=3776AB"/></a>
  <a href="https://pypi.org/project/discord.py/" target="_blank"><img src="https://img.shields.io/badge/discord.py-2.4.0-grey?style=flat-square&logo=discord&logoColor=white&color=5865F2"/></a>
  <a href="https://github.com/TheGreatAlphaA/Maple-bot/blob/main/LICENSE" target="_blank"><img src="https://img.shields.io/badge/license-MIT-grey?style=flat-square&color=green"/></a>
</p>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#download">Download</a> •
  <a href="#credits">Credits</a> •
  <a href="#license">License</a>
</p>

## Key Features
<span id="key-features"></span>

* Music Player
  - Enter keywords to add music content to the queue.
  - Pause, skip, remove, and resume playing music at any time.
* Remind Me
  - Use natural language to set reminders in the near or distant future.
* Keyword Tracking
  - Set up keyword lists to listen for messages.
  - Ideal for monitoring announcement channels that publish sales or product restocks.
* Dungeons and Dragons
  - Roll dice with as many sides as you need.
  - Combine groups of dice to get results quickly when you need it.
  - Roll dice for groups of creatures; perfect for summoning-based builds.
* YouTube Notifications
  - Requires YouTube API Key
  - Get notified when channels post new videos
  - Sort videos into multiple channels with tags!
* Stock Market Tracker
  - Requires Alpha Vantage API key for stocks.
  - Requires Gold-Api.io key for metals.
  - Get notifications when your stocks hit their buy or sell targets!
* Hypixel Skyblock Tracker
  - Requires Hypixel API Key
  - Track your progress against other players on the collections leaderboard!
  - Get reminders to collect your minions when they are full.

## How To Use
<span id="how-to-use"></span>

To clone and run this application, you'll need [Git](https://git-scm.com), [Python 3.9+](https://www.python.org/downloads/), and [FFmpeg](https://ffmpeg.org/download.html)  installed on your computer. You will also need a MySQL database installed and accessible from your local network. From your command line:

#### Installing the required dependancies
```bash
# Install Git
$ sudo apt install git

# Install Python 3 (latest version)
$ sudo apt install python3.12-venv

# Install FFmpeg
$ sudo apt install ffmpeg
```

> **Note**
> If you're using Windows, use the following links to download the required dependancies:
- [Git for Windows](https://git-scm.com/downloads/win)
- [Python 3 for Windows](https://www.python.org/downloads/windows/)
- [FFmpeg for Windows](https://www.wikihow.com/Install-FFmpeg-on-Windows)

  
#### Installing the application
```bash
# Clone this repository
$ git clone https://github.com/TheGreatAlphaA/Maple-bot

# Go into the repository
$ cd maple-bot

# Create a virtual environment
$ python3 -m venv venv

# Activate the virtual environment
$ source venv/bin/activate

# Install dependencies
$ sudo pip install -r requirements.txt
```

#### Configuring the application
Start by taking the provided info.ini._template file and rename it to info.ini. You will need to set up multiple configuration options before the first run. 
```bash
[BOT]
discord_bot_token = # https://discord.com/developers
enable_skyblock_tracker = FALSE
enable_keyword_tracker = FALSE
enable_network_tracker = FALSE # only enable this if you know what you're doing!
enable_finance_tracker = FALSE
enable_reminders = FALSE
enable_youtube_notifications = FALSE
```
First, start by obtaining a discord bot token. Determine which features you need to enable; keep in mind that some options require additional API keys to function.
```bash
[DATABASE]
host = 
user = 
password = 
database = 
```
If you have an existing MySQL database server, you can enter your information here. Otherwise, follow this guide to set up: [Getting started with MySQL](https://dev.mysql.com/doc/mysql-getting-started/en/)
```bash
[SKYBLOCK]
hypixel_api_key = # https://developer.hypixel.net/
```
To use the Skyblock functions, you will need to register your application with Hypixel to obtain an API key.
```bash
[NOTIFICATIONS]
youtube_api_key = # https://developers.google.com/youtube/v3/getting-started
```
To use the YouTube Notifications feature, you will need to register for an API key with Google.
```bash
[FINANCE]
alpha_vantage_api_key = # https://www.alphavantage.co/support/#api-key
gold_api_key = # https://www.goldapi.io/
```
To use the Financial Tracker, you will need to register for an API key with Alpha Vantage and Gold API
```bash
[DISCORD_CHANNELS]
bot_commands = 
security_news = 
gaming_news = 
pc_hardware_news = 
educational_news = 
celebrity_news = 
deals = 
deal_tracker = 
skyblock_tracker = 
stock_tracker = 
network_tracker = 

[DISCORD_ROLES]
bot_commands_role = 
deal_notifications = 
security_news = 
gaming_news = 
pc_hardware_news = 
educational_news = 
celebrity_news = 
```
For the Discord Channels and Roles, enter the channel ids and role ids for each appropriate channel and role respectively.

#### Run the application
```bash
# Run the app
$ python main.py
```

## Download
<span id="Download"></span>

You can [download](https://github.com/TheGreatAlphaA/Maple-bot/releases/latest) the latest version of Maple-Bot.

## Credits
<span id="Credits"></span>

This software uses the following open source packages:

- [dateparser](https://pypi.org/project/dateparser/)
- [discord.py](https://pypi.org/project/discord.py/)
- [humanfriendly](https://pypi.org/project/humanfriendly/)
- [mysql-connector-python](https://pypi.org/project/mysql-connector-python/)
- [table2ascii](https://pypi.org/project/table2ascii/)
- [urllib3](https://pypi.org/project/urllib3/)
- [youtube-search-python](https://pypi.org/project/youtube-search-python/)
- [yt-dlp](https://pypi.org/project/yt-dlp/)
- [wakeonlan](https://pypi.org/project/wakeonlan/)

## License
<span id="License"></span>

MIT

---
