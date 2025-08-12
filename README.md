# 🎵 Spotify Weekly Releases

A personal tool that automatically creates weekly playlists featuring new releases from your followed Spotify artists and similar artists you might enjoy.

## Features

- 🎯 **Smart Discovery**: Scans your followed artists for new releases
- 🔍 **Artist Expansion**: Finds similar artists and includes their latest tracks  
- ⏰ **Weekly Automation**: Filters for releases from the past 7 days
- 🎵 **Playlist Creation**: Automatically generates and populates playlists
- 🔒 **Secure Auth**: Uses OAuth 2.0 for secure Spotify API access

## Setup

### 1. Spotify Developer Account
1. Visit [developer.spotify.com](https://developer.spotify.com)
2. Create a new app with these settings:
   - **Website**: `https://yourusername.github.io/spotify-weekly-releases`
   - **Redirect URI**: `https://yourusername.github.io/spotify-weekly-releases/callback.html`

### 2. Required Scopes
The application requires these Spotify API scopes:
- `user-follow-read` - Read your followed artists
- `playlist-modify-public` - Create public playlists
- `playlist-modify-private` - Create private playlists

### 3. Installation
```bash
git clone https://github.com/yourusername/spotify-weekly-releases.git
cd spotify-weekly-releases
pip install -r requirements.txt
```

### 4. Configuration
Create a `.env` file with your Spotify credentials:
```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=https://yourusername.github.io/spotify-weekly-releases/callback.html
```

## Usage

```bash
python spotify_weekly.py
```

The script will:
1. Open your browser for Spotify authentication
2. Scan your followed artists
3. Find similar artists and recent releases
4. Create a new playlist with this week's discoveries

## Project Structure

```
spotify-weekly-releases/
├── README.md           # Project documentation
├── index.html          # Project website
├── callback.html       # OAuth callback handler
├── requirements.txt    # Python dependencies
├── spotify_weekly.py   # Main application script
├── .env               # Configuration (create this)
└── .gitignore         # Git ignore rules
```

## Development Status

🚧 **Currently in Development**

This is a personal project for music discovery. The tool is in active development and currently supports:
- [x] Spotify API authentication
- [x] GitHub Pages hosting setup
- [ ] Artist following analysis
- [ ] Similar artist discovery
- [ ] New release detection
- [ ] Playlist creation
- [ ] Automated scheduling

## Contributing

This is a personal project, but feel free to fork and adapt for your own use!

## License

MIT License - Feel free to use and modify for personal use.

## Disclaimer

This project is not affiliated with Spotify. It uses the Spotify Web API under their terms of service.
