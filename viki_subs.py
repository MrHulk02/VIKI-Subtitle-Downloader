import argparse
import math
import os
import re
import requests
from requests.exceptions import HTTPError

INFO = "https://api.viki.io/v4/containers/{pageid}.json"
SERIES = "https://api.viki.io/v4/containers/{pageid}/episodes.json"
SUBTITLE = "https://api.viki.io/v4/videos/{vid_id}/auth_subtitles/{lang}.srt"
HEADERS = {
    'Referer': 'https://www.viki.com/',
    'X-Viki-App-Ver': '2.151.1',
    'X-Viki-Device-ID': '239083520d',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
}


class VIKI:
    def __init__(self, url: str, episode: str, language: str):
        match = re.search(r"/(tv|movies)/([0-9]{2,9}[vc])", url)
        if not match:
            raise ValueError("[-] Invalid URL. Please use series or movie URL.")
        self.id = match.group(2)
        self.episode = episode
        self.language = language.lower()
        self._type = None
        self.app = "100000a"
    
    def get_titles(self):
        res = requests.get(
            url=INFO.format(pageid=self.id),
            params={"app": self.app},
            headers=HEADERS
            )
        res = self.is_valid(res, "title")
        
        self._type = res.get("type")
        title = res.get("titles", {}).get("en")
        title_id = res.get("id") if self._type == "series" else res.get("watch_now", {}).get("id")
        total_episodes = res.get("planned_episodes") if res.get("episodes", {}).get("count") == 0 else res.get("episodes", {}).get("count")

        print(f"[+] ID: {title_id}")
        print(f"[+] Title: {title}")
        print(f"[+] Type: {self._type}")

        if self._type in ["movie", "film"]:
            return [{
                '_id': title_id,
                'title': title,
                'subtitle': [lang for lang, percent in res.get("subtitle_completions", {}).items() if percent > 90]
                }]
        else:
            titles = []
            i = 1
            while i < math.ceil(total_episodes / 50) + 1:
                vid = requests.get(
                    url=SERIES.format(pageid=self.id),
                    params={
                        'direction': 'asc',
                        'with_upcoming': 'true',
                        'sort': 'number',
                        'blocked': 'true',
                        'only_ids': 'false',
                        'app': self.app,
                        'page': i,
                        'per_page': '50',
                    },
                    headers=HEADERS
                )
                vid = self.is_valid(vid, "video list")
                i += 1
                for episode in vid.get("response", []):
                    if not self.in_range(episode.get("number")):
                        continue

                    titles.append({
                        '_id': episode.get("id"),
                        'title': title,
                        'episode': episode.get("number"),
                        'subtitle': [lang for lang, percent in episode.get("subtitle_completions", {}).items() if percent > 90]
                    })
            return titles
    
    def get_subtitle(self):
        data = self.get_titles()
        
        for sub in data:
            if self._type == "series":
                title = f"{sub.get('title')}.S01E{sub.get('episode'):02d}".replace(' ', '.')
            else:
                title = sub.get('title').replace(' ', '.')

            if self.language not in sub.get("subtitle") and not self.language == "all":
                raise ValueError(f"'{self.language}' subtitle is not available. These are the available subtitles: {sub['subtitle']}")
            for lang in sub.get("subtitle"):
                if self.language != "all" and lang != self.language:
                    continue
                self.download_subtitle(sub.get("_id"), title, lang)

    def download_subtitle(self, sub_id, title, lang):
        res = requests.get(
            url=SUBTITLE.format(vid_id=sub_id, lang=lang),
            params={"app": self.app},
            headers=HEADERS
        )

        output = os.path.join(os.getcwd(), "output")
        os.makedirs(output, exist_ok=True)

        if res.status_code == 200:
            filename = os.path.join(output, f'{title}.{lang}.srt')
            with open(filename, 'wb') as subtitle_file:
                subtitle_file.write(res.content)
            print(f"[+] Downloaded: {filename}")
        else:
            print(f"[-] Failed to download subtitle for video ID {sub_id}, language {lang}")

    def is_valid(self, res, stage):
        try:
            res.raise_for_status()
            return res.json()
        except HTTPError as e:
            raise HTTPError(f"[-] HTTP error during {stage}: {e}")
        except ValueError as e:
            raise ValueError(f"[-] JSON decode error during {stage}: {e}")

    def in_range(self, episode_num):
        if not self.episode:
            return True
        if '-' in self.episode:
            start, end = map(int, self.episode.split('-'))
            return start <= episode_num <= end
        if self.episode.isdigit():
            return episode_num == int(self.episode)
        return False

if __name__ == "__main__":
    parse = argparse.ArgumentParser(prog="VIKI subtitles download")
    parse.add_argument("url", type=str, help="viki url.")
    parse.add_argument("-e", "--episode", type=str, default=None, help="Episode number (e.g., 1 or range 1-5)")
    parse.add_argument("-l", "--language", type=str, default="all", help="Subtitle language (e.g., en or all)")
    
    args = parse.parse_args()
    start = VIKI(args.url, args.episode, args.language)
    start.get_subtitle()