# The World in One Day — Wednesday 25 November 2026

[![news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/c/news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/kyamano/news-image-20261125/rank.svg)](https://make.fun/c/news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/kyamano/news-image-20261125/reward.svg)](https://make.fun/c/news-image-20261125)

A newspaper front page for one day of world news: 25 November 2026.
Ten stories in depth, twenty more in brief — tariffs, the Strait of
Hormuz, a first Pakistani astronaut, a Pacific pact, a controlled blast
in Iowa, a tanker fire in Cairo, and the AI rally running out of steam.

## How it is made

`main.py` draws the whole page from scratch with the Python 3 standard
library only. It embeds a small 5x7 bitmap font, paints the masthead,
a wireframe globe, nine story cards and the briefs strip, and writes a
PNG with zlib. No network, no photos, no files read.

Run it twice and the output is byte-identical:

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Files

- `main.py` — the program that draws `entry.png`
- `entry.png` — the image, 1024x1024, under 1 MiB

## Sources

Reuters, AP, AFP, Al Jazeera, CNN, BBC, The Hindu, Nikkei, SCMP, NYT
and WSJ, all reporting on 25 November 2026. Each story was checked
against at least two outlets; items whose date fell on 24 November or
earlier were left out.

## License

MIT. See `LICENSE`.
