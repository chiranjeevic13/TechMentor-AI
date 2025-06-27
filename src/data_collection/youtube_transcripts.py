# YouTube transcript fetcher
import os
import logging
from typing import List, Dict, Any
import yaml
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import re
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeTranscriptFetcher:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the YouTube transcript fetcher with configuration."""
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)["data_collection"]
        
        self.output_dir = "data/raw/youtube"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _get_video_ids_from_channel(self, channel_name: str, max_videos: int = 10) -> List[str]:
        """Get video IDs from a YouTube channel using channel name."""
        # This is a simplified approach - in a production system you'd use the YouTube API
        # For a free solution, we'll scrape the channel page
        try:
            channel_url = f"https://www.youtube.com/@{channel_name}/videos"
            response = requests.get(channel_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            # Extract video IDs using regex
            video_ids = re.findall(r'watch\?v=([a-zA-Z0-9_-]{11})', response.text)
            # Remove duplicates while maintaining order
            unique_video_ids = []
            for vid in video_ids:
                if vid not in unique_video_ids:
                    unique_video_ids.append(vid)
            
            return unique_video_ids[:max_videos]
        except Exception as e:
            logger.error(f"Error getting videos from channel {channel_name}: {str(e)}")
            return []
    
    def fetch_transcripts(self) -> List[Dict[str, Any]]:
        """Fetch transcripts from YouTube videos of configured channels."""
        results = []
        
        youtube_sources = [source for source in self.config["sources"] if source["type"] == "youtube"]
        for source in youtube_sources:
            for channel in source.get("channels", []):
                try:
                    logger.info(f"Getting videos from channel: {channel}")
                    video_ids = self._get_video_ids_from_channel(channel)
                    
                    for video_id in video_ids:
                        try:
                            logger.info(f"Fetching transcript for video: {video_id}")
                            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                            
                            # Combine transcript parts
                            full_transcript = ""
                            for part in transcript_list:
                                full_transcript += part["text"] + " "
                            
                            # Get video title (optional)
                            video_title = f"Video_{video_id}"
                            
                            # Save the transcript
                            output_path = os.path.join(self.output_dir, f"{video_title}.txt")
                            with open(output_path, "w", encoding="utf-8") as f:
                                f.write(f"Source: https://www.youtube.com/watch?v={video_id}\n")
                                f.write(f"Channel: {channel}\n\n")
                                f.write(full_transcript)
                            
                            results.append({
                                "video_id": video_id,
                                "channel": channel,
                                "output_path": output_path,
                                "content_length": len(full_transcript)
                            })
                            
                            # Be nice to YouTube
                            time.sleep(1)
                            
                        except Exception as e:
                            logger.error(f"Error fetching transcript for video {video_id}: {str(e)}")
                
                except Exception as e:
                    logger.error(f"Error processing channel {channel}: {str(e)}")
        
        return results

if __name__ == "__main__":
    fetcher = YouTubeTranscriptFetcher()
    results = fetcher.fetch_transcripts()
    logger.info(f"Fetched {len(results)} video transcripts")