# VIKI Subtitle Downloader

A Python script to download subtitles (`.srt`) from [Viki.com](https://www.viki.com).

## Features

- Supports both movies and series.
- Download subtitles for a specific episode, a range of episodes, or all.
- Filter subtitles by language.
- Saves `.srt` files to the `output/` folder.

## Requirements

- Python 3.7+
- `requests` module (install via `pip install requests`)

## Usage

```bash
python viki_subs.py <viki_url> [-e EPISODE] [-l LANGUAGE]
```

### Arguments

- `<viki_url>` – URL of the movie or series from Viki (required).
- `-e`, `--episode` – Specific episode number or range (e.g., `5` or `1-5`). Optional.
- `-l`, `--language` – Subtitle language code (e.g., `en`, `fr`, `all`). Defaults to `all`.

### Examples

Download English subtitles from a movie:

```bash
python viki_subs.py "https://www.viki.com/movies/6246c-sunk-into-her" -l en
```

Download English subtitles for episodes 1 to 3 of a series:

```bash
python viki_subs.py "https://www.viki.com/tv/35817c-ashes-of-love" -e 1-3 -l en
```

Download all available subtitles for all episodes:

```bash
python viki_subs.py "https://www.viki.com/tv/35817c-ashes-of-love"
```

## Output

Subtitles are saved in the `./output` folder using the following format:

- For series:
  ```
  <Title>.S01E<Number>.<Language>.srt
  ```

- For movies:
  ```
  <Title>.<Language>.srt
  ```

## Disclaimer

This script is intended for educational and personal use only.
