#!/usr/bin/env python3
"""
My Music Discovery Tool
Creates playlists with new releases from followed artists and similar artists
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Set
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MusicDiscoveryTool:
    def __init__(self):
        """Initialize the Spotify client with authentication"""
        self.setup_spotify_client()
        self.user_id = None
        self.days_lookback = int(os.getenv('DAYS_LOOKBACK', 7))
        self.max_tracks = int(os.getenv('MAX_TRACKS_PER_PLAYLIST', 50))
        self.playlist_prefix = os.getenv('PLAYLIST_NAME_PREFIX', 'Weekly Discoveries')
        
    def setup_spotify_client(self):
        """Set up Spotify client with OAuth authentication"""
        try:
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
            
            if not all([client_id, client_secret, redirect_uri]):
                raise ValueError("Missing Spotify API credentials in .env file")
            
            # Define required scopes
            scope = [
                'user-follow-read',          # Read followed artists
                'playlist-modify-public',    # Create public playlists
                'playlist-modify-private',   # Create private playlists
                'user-library-read'          # Read user's library
            ]
            
            # Set up OAuth
            auth_manager = SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=' '.join(scope),
                cache_path='.spotify_cache'
            )
            
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            
            # Get current user info
            user_info = self.sp.current_user()
            self.user_id = user_info['id']
            print(f"✅ Successfully authenticated as: {user_info['display_name']}")
            
        except Exception as e:
            print(f"❌ Error setting up Spotify client: {e}")
            sys.exit(1)
    
    def get_followed_artists(self) -> List[Dict]:
        """Get all artists the user follows"""
        print("🎵 Fetching your followed artists...")
        
        artists = []
        results = self.sp.current_user_followed_artists(limit=50)
        
        while results:
            artists.extend(results['artists']['items'])
            if results['artists']['next']:
                results = self.sp.next(results['artists'])
            else:
                break
        
        print(f"📊 Found {len(artists)} followed artists")
        return artists
    
    def get_similar_artists(self, artist_ids: List[str], max_similar: int = 20) -> List[Dict]:
        """Get similar artists for discovery"""
        print("🔍 Finding similar artists for discovery...")
        
        similar_artists = []
        seen_ids = set(artist_ids)  # Don't include artists we already follow
        
        # Get similar artists for a sample of followed artists
        sample_size = min(10, len(artist_ids))  # Limit API calls
        
        for i, artist_id in enumerate(artist_ids[:sample_size]):
            try:
                related = self.sp.artist_related_artists(artist_id)
                
                for artist in related['artists']:
                    if artist['id'] not in seen_ids and len(similar_artists) < max_similar:
                        similar_artists.append(artist)
                        seen_ids.add(artist['id'])
                
                print(f"📈 Progress: {i+1}/{sample_size} artists processed")
                
            except Exception as e:
                print(f"⚠️  Error getting similar artists for {artist_id}: {e}")
                continue
        
        print(f"🎯 Found {len(similar_artists)} similar artists")
        return similar_artists
    
    def get_recent_releases(self, artists: List[Dict]) -> List[Dict]:
        """Get recent releases from artists"""
        print(f"🆕 Checking for releases in the last {self.days_lookback} days...")
        
        cutoff_date = datetime.now() - timedelta(days=self.days_lookback)
        recent_tracks = []
        
        for i, artist in enumerate(artists):
            try:
                # Get artist's albums (including singles)
                albums = self.sp.artist_albums(
                    artist['id'], 
                    album_type='album,single', 
                    limit=10,
                    country='US'
                )
                
                for album in albums['items']:
                    # Check if album is recent
                    try:
                        release_date = datetime.strptime(album['release_date'], '%Y-%m-%d')
                    except ValueError:
                        # Handle partial dates like '2024' or '2024-01'
                        if len(album['release_date']) == 4:  # Year only
                            release_date = datetime.strptime(f"{album['release_date']}-01-01", '%Y-%m-%d')
                        elif len(album['release_date']) == 7:  # Year-Month
                            release_date = datetime.strptime(f"{album['release_date']}-01", '%Y-%m-%d')
                        else:
                            continue
                    
                    if release_date >= cutoff_date:
                        # Get tracks from this album
                        tracks = self.sp.album_tracks(album['id'])
                        
                        for track in tracks['items']:
                            track_info = {
                                'id': track['id'],
                                'name': track['name'],
                                'artist': artist['name'],
                                'album': album['name'],
                                'release_date': album['release_date'],
                                'uri': track['uri']
                            }
                            recent_tracks.append(track_info)
                
                # Progress indicator
                if (i + 1) % 10 == 0:
                    print(f"📊 Progress: {i+1}/{len(artists)} artists checked")
                
            except Exception as e:
                print(f"⚠️  Error checking releases for {artist['name']}: {e}")
                continue
        
        # Remove duplicates and limit results
        seen_tracks = set()
        unique_tracks = []
        
        for track in recent_tracks:
            track_key = (track['name'].lower(), track['artist'].lower())
            if track_key not in seen_tracks:
                seen_tracks.add(track_key)
                unique_tracks.append(track)
        
        # Sort by release date (newest first)
        unique_tracks.sort(key=lambda x: x['release_date'], reverse=True)
        
        print(f"🎵 Found {len(unique_tracks)} recent tracks")
        return unique_tracks[:self.max_tracks]
    
    def create_playlist(self, tracks: List[Dict]) -> str:
        """Create a new playlist with the discovered tracks"""
        if not tracks:
            print("❌ No tracks to add to playlist")
            return None
        
        # Generate playlist name with current date
        today = datetime.now()
        playlist_name = f"{self.playlist_prefix} - {today.strftime('%B %d, %Y')}"
        
        # Create playlist description
        description = (
            f"New releases from your followed artists and similar artists "
            f"from the past {self.days_lookback} days. "
            f"Generated on {today.strftime('%Y-%m-%d')}"
        )
        
        try:
            # Create the playlist
            playlist = self.sp.user_playlist_create(
                user=self.user_id,
                name=playlist_name,
                public=False,  # Private by default
                description=description
            )
            
            # Add tracks to playlist
            track_uris = [track['uri'] for track in tracks]
            
            # Spotify limits to 100 tracks per request
            for i in range(0, len(track_uris), 100):
                batch = track_uris[i:i+100]
                self.sp.playlist_add_items(playlist['id'], batch)
            
            print(f"✅ Created playlist: '{playlist_name}' with {len(tracks)} tracks")
            print(f"🔗 Playlist URL: {playlist['external_urls']['spotify']}")
            
            return playlist['id']
            
        except Exception as e:
            print(f"❌ Error creating playlist: {e}")
            return None
    
    def print_track_summary(self, tracks: List[Dict]):
        """Print a summary of discovered tracks"""
        if not tracks:
            print("📭 No new releases found this week")
            return
        
        print(f"\n🎵 Found {len(tracks)} New Releases:")
        print("-" * 60)
        
        for i, track in enumerate(tracks[:10], 1):  # Show first 10
            print(f"{i:2d}. {track['name']}")
            print(f"    by {track['artist']} • {track['album']}")
            print(f"    Released: {track['release_date']}")
            print()
        
        if len(tracks) > 10:
            print(f"... and {len(tracks) - 10} more tracks")
    
    def run(self):
        """Main execution flow"""
        print("🚀 Starting My Music Discovery Tool")
        print("=" * 50)
        
        try:
            # Step 1: Get followed artists
            followed_artists = self.get_followed_artists()
            if not followed_artists:
                print("❌ No followed artists found. Please follow some artists on Spotify first.")
                return
            
            # Step 2: Get similar artists for discovery
            followed_ids = [artist['id'] for artist in followed_artists]
            similar_artists = self.get_similar_artists(followed_ids)
            
            # Combine both lists
            all_artists = followed_artists + similar_artists
            
            # Step 3: Find recent releases
            recent_tracks = self.get_recent_releases(all_artists)
            
            # Step 4: Show summary
            self.print_track_summary(recent_tracks)
            
            # Step 5: Create playlist if tracks found
            if recent_tracks:
                playlist_id = self.create_playlist(recent_tracks)
                if playlist_id:
                    print("\n🎉 Success! Your weekly playlist is ready!")
                else:
                    print("\n❌ Failed to create playlist")
            else:
                print("\n📭 No new releases this week. Check back later!")
        
        except KeyboardInterrupt:
            print("\n⏹️  Process interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

def main():
    """Entry point"""
    print("🎵 My Music Discovery Tool")
    print("Discover new music from your followed artists!\n")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ Error: .env file not found!")
        print("Please create a .env file with your Spotify API credentials.")
        print("See .env.example for the required format.")
        return
    
    # Initialize and run the tool
    tool = MusicDiscoveryTool()
    tool.run()

if __name__ == "__main__":
    main()