# Promotional assets

- `quotaguard-promo.mp4`: 1920 x 1080, 24 fps, approximately 49 seconds.
- `quotaguard-promo.en.srt`: English subtitle track; captions are also burned into the video.
- `poster.png`: README poster.
- `scenes.json`: English narration and scene headings.
- `voice-*.mp3`: synthetic English narration, en-US-GuyNeural.

All quota examples are simulated. This is an illustrative product explainer,
not a recording of the ChatGPT interface or a measured productivity study.
There is no background music. Graphics are programmatically drawn.

To regenerate the visuals with the supplied narration:

```sh
python -m pip install Pillow imageio-ffmpeg
python scripts/create_video.py
```

The skill itself does not need these media dependencies.
