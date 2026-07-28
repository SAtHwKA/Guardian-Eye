# Guardian Eye

An AI Safety Sentinel for Blast Zones — real-time person detection, danger-zone reasoning, and blast-control gating, powered by Gemma 4.

Build with Gemma 4 — AI Durg (Open Track)

Team: Mamidipalli Sathwika, Vangapaty Sree Krishna, Reva Thatikonda

## The Problem

On mining and blasting sites, the single most dangerous failure mode isn't equipment — it's a person being in the wrong place at the wrong time. A worker who wanders into a blast radius during a countdown, or who is missing required safety gear near a restricted zone, is a fatality risk that a human monitor watching a bank of CCTV feeds can easily miss.

Guardian Eye is a camera-based sentinel that watches restricted zones continuously, reasons about what it sees using Gemma 4, and has the authority to halt a blast countdown the instant it detects a violation.

It operates across two modes:

- **Pre-Blast Verification Mode** — before the countdown is armed, the system confirms the danger zone is clear. If a person is detected, the timer is locked until re-verified as clear.
- **Active Blast Countdown Mode** — once armed, detecting a person triggers an immediate abort of the live countdown.

## Architecture

Guardian Eye is a three-stage pipeline:

**1. Perception** (`perception/perception.py`)
YOLOv8 runs on each frame of the live camera feed (or an uploaded CCTV clip). For every detected person, the bounding box is checked against a configurable danger-zone polygon, and the person is cropped out for closer inspection.

**2. Intelligence** (`brain/brain.py`)
Gemma 4 receives the cropped image context along with the person's zone status (restricted vs. safe) and reasons about the situation, grounded by a RAG step over the site's Safety Manual PDF. Gemma returns a structured verdict — CRITICAL (person in the blast radius) or COMPLIANCE (a PPE/procedural gap) — with a plain-language reason.

**3. Action** (`action/action_interface.py`, `action/main.py`)
A Streamlit "Command Center" dashboard consumes Gemma's verdicts in real time. A CRITICAL verdict aborts an in-progress blast countdown and locks the start control until the area is confirmed clear. Role-based access (Manager vs. Employee) restricts who can arm the countdown or trigger the site buzzer.

## How Gemma 4 Is Used

- **Grounded reasoning via RAG** — relevant passages from the actual safety manual PDF are retrieved and injected into the prompt, so verdicts trace back to real, site-specific policy rather than a generic notion of safety.
- **Structured decision output** — the prompt constrains Gemma to a strict JSON contract (priority, msg, reason, identity), letting the dashboard consume its output programmatically and drive a real control-flow decision.
- **Severity classification tied to physical context** — the same prompt handles CRITICAL zone intrusions and COMPLIANCE gaps, using the danger-zone boolean from the perception layer as grounding context.

## Design Decision: Separating Geometry from Judgment

YOLOv8 and polygon math handle the deterministic geometric question — is this bounding box inside the restricted area. Gemma 4 handles the judgment question — given this situation and our actual safety rules, what should happen. Each component does what it's actually good at: a vision-language model guessing pixel coordinates is a worse detector than a purpose-built detection model, and a hardcoded rule engine is a worse judge of nuanced compliance questions than an LLM grounded in real policy text.

## Repository Structure

```
guardian-eye/
├── perception/
│   └── perception.py       # YOLOv8 detection + danger-zone polygon check
├── brain/
│   └── brain.py            # Gemma 4 reasoning + RAG over safety manual
├── action/
│   ├── action_interface.py # Blast state machine: lock / arm / abort
│   └── main.py             # Streamlit Command Center dashboard
├── manuals/
│   └── safety_manual.pdf   # Site safety manual used for RAG grounding
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/guardian-eye.git
cd guardian-eye
pip install -r requirements.txt
```

Create a `.env` file in the project root (git-ignored, never committed):

```
GEMMA_API_KEY=your_key_here
```

## Running the App

```bash
streamlit run action/main.py
```

The dashboard defaults to CCTV disconnected on every login — an operator must explicitly grant camera access each session rather than monitoring silently running by default.

## Demo Credentials

Fixed demonstration credentials for hackathon evaluation only, scoped to a local/sandboxed instance. Not production secrets.

| Role | Capabilities |
|---|---|---|---|
| Manager | Connect/disconnect CCTV, trigger buzzer, arm/abort blast countdown, view alerts |
| Employee | View live feed and redacted safety log, no blast control |

## Safety, Access, and Accountability

- Only Manager-role users can arm the blast countdown or manually trigger the site-wide buzzer; Employee-role logins can view alerts but not control the blast sequence.
- Every CRITICAL verdict is logged with a timestamp and reason, and stays visible in the on-screen safety log for the shift.
- The dashboard defaults to CCTV disconnected on every login.

## License

MIT — see [LICENSE](LICENSE) for details.
