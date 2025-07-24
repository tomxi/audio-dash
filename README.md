---
title: Music Structure Analysis Dashboard
emoji: 🎶
colorFrom: indigo
colorTo: green
sdk: docker
app_file: app.py
pinned: false
---

# audio-dash
Audio dashborad hosted on huggingface spaces using dash and plotly

run locally with:
```bash
docker-compose up dev
```

then visit http://localhost:7860

to rebuild the image, run:
```bash
docker build -t audio-dash .
```
