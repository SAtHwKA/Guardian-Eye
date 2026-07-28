# Guardian Eye — Phase 1 → Phase 2 Handoff

**From:** Reva (Perception)
**To:** Krishna (Intelligence)

This is the output format from the Perception pipeline. Use this to build the
Gemma 4 reasoning layer against.

---

## Folder structure

Each processed video gets its own subfolder under `candidates/`, named after
the video file:

```
guardian_eye_output/
└── candidates/
    ├── V1/
    │   ├── frame0_person1.jpg
    │   ├── frame0_person2.jpg
    │   ├── frame5_person3.jpg
    │   ├── ...
    │   └── manifest.json
    └── V2/
        ├── frame0_person1.jpg
        ├── ...
        └── manifest.json
```

- Each `.jpg` is a **cropped image of one detected person** in one frame.
- `manifest.json` describes every detection in that video — this is the file
  you'll parse.

---

## manifest.json format

```json
{
  "video_source": "V1.mp4",
  "generated_at": "2026-07-20T14:32:10.123456",
  "frame_width": 1280,
  "frame_height": 720,
  "danger_zone_polygon": [[640, 0], [1280, 0], [1280, 720], [640, 720]],
  "total_frames_processed": 315,
  "total_detections": 127,
  "detections": [
    {
      "frame_id": 245,
      "timestamp_sec": 9.8,
      "person_id": 99,
      "bbox": {"x1": 512, "y1": 88, "x2": 701, "y2": 640},
      "confidence": 0.90,
      "image_path": "guardian_eye_output/candidates/V1/frame245_person99.jpg",
      "in_danger_zone": true
    }
  ]
}
```

### Field reference

| Field | Meaning |
|---|---|
| `danger_zone_polygon` | Pixel coordinates of the restricted zone for this video. Currently the right half of the frame (placeholder — will change per real camera setup). |
| `frame_id` | Which frame in the video this detection came from. |
| `timestamp_sec` | Time in the video (seconds) this detection occurred. |
| `person_id` | Unique ID per detection (not tracked across frames yet — same person walking through multiple frames gets a new ID each time). |
| `bbox` | Pixel coordinates of the person's bounding box in the original frame. |
| `confidence` | YOLOv8 detection confidence (0–1). We filter below 0.5. |
| `image_path` | Path to the cropped image of just this person — feed this into Gemma for PPE/violation analysis. |
| `in_danger_zone` | `true` if the person's foot position falls inside the danger zone polygon. |

---

## What Krishna needs to build (Phase 2)

1. Read `manifest.json` for a video.
2. For each detection, load the cropped image at `image_path`.
3. Send the image to Gemma 4 (via Google AI Studio API) with a prompt asking
   it to check for PPE compliance (helmet/vest) — combine with
   `in_danger_zone` to decide severity.
4. Cross-reference the Safety Manual PDF via RAG for the specific rule being
   violated.
5. Output a structured JSON decision, e.g.:

```json
{
  "person_id": 99,
  "violation": "no_helmet",
  "in_danger_zone": true,
  "action": "LOCK_TIMER",
  "reasoning": "..."
}
```

---

## Known limitations (Reva's side, WIP)

- **No person tracking yet** — same person across frames = different
  `person_id`. If Krishna needs continuity (e.g. "this same person has been
  in the zone for 10 seconds"), flag it — tracking (e.g. simple IoU-based ID
  matching or ByteTrack) can be added.
- **Danger zone is a placeholder** (right half of frame) — will be replaced
  with real camera-specific coordinates before final integration.
- **Frame sampling** — currently every 5th frame (~5 fps at 25fps source).
  Adjustable if Gemma needs denser or sparser sampling.
