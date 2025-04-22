<h1 align="center">Visivox</h1>
<p align="center">
  Hands‑free Multimodal Assistive Control
</p>

<a href="https://hack36.com"> <img src="https://i.postimg.cc/FFwvfkGk/built-at-hack36.png" height="24px"> </a>

## Introduction:

Visivox is an open‑source application that empowers users—especially those with mobility impairments—to control their computer hands‑free by combining webcam‑based gaze, facial‑gesture detection, and voice commands into precise OS actions.

## Demo Video Link:

<a href="https://drive.google.com/file/d/1dilaH49qEH4ohXKP_anlWjV6fUwUrr1K/view?usp=sharing">Video Link</a>

## Presentation Link:

<a href="https://drive.google.com/file/d/1cgk_5PRYWrMsmF7LbtpS3gOTfrQa4rTh/view?usp=sharing">PPT link here</a>

## Table of Contents:

- [Introduction](#introduction)
- [Problem Statement](#problem-statement)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Usage](#usage)
- [Contributors](#contributors)

## Problem Statement:

Millions with mobility impairments (ALS, paralysis, RSI) struggle with traditional input devices. Voice‑only solutions lack precision for complex tasks. Visivox fills this gap with multimodal voice + gaze + facial gestures for versatile, real‑time control.

## Features:

1. **Cursor Control via Gaze** – Move your head to steer the pointer
2. **Single & Double Clicks** – Blink once to click, twice quickly to double‑click
3. **Right‑Click** – Raise eyebrow gesture
4. **Scrolling** – Open mouth + head movement to scroll up/down/left/right
5. **Drag & Drop** – Hold mouth‑open gesture to drag, close to release
6. **Voice Commands** – “Open Notepad,” “Go to example.com,” “Type Hello,” “Press Ctrl+S”
7. **Customizable Settings** – Adjust sensitivity, blink thresholds, scroll speed via GUI

## Integration with Julep AI

VisoVox now harnesses **Julep AI’s chat‑context remembering** feature to keep track of our design decisions, model parameters, and debugging threads across multiple sessions.

- **Seamless Context Retention:** No more repeating prompts—Julep AI recalls prior exchanges end‑to‑end, cutting down redundant back‑and‑forth by over 80%.
- **Faster Iteration:** Prototyping new audio‑visual gestures went from days to hours, thanks to instant access to our last conversations and code snippets.
- **Reduced Debugging Time:** By preserving error histories and fix attempts, Julep AI has slashed troubleshooting efforts by roughly 50%, saving the team dozens of hours so far.

Overall, Julep AI’s memory feature has been a game‑changer—enabling uninterrupted workflows, accelerating feature roll‑out, and keeping our focus on innovation rather than repetition.

## Technology Stack:

1. **Computer Vision:** OpenCV, MediaPipe
2. **Speech Recognition:** Google Cloud Speech‑to‑Text, `speech_recognition`
3. **Automation & Controls:** PyAutoGUI, `keyboard`, Windows Accessibility APIs
4. **Language & Frameworks:** Python 3.x, Tkinter
5. **LLM & Context:** Julep API (GPT‑4o)
6. **Configuration:** `python-dotenv`, YAML

## Usage:

1. **Clone & Install**
   ```bash
   git clone https://github.com/pratik4505/visivox.git
   cd visivox
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **Configure**
   - Copy `.env.example` to `.env` and set your `JULEP_API_KEY`, `GEMINI_API_KEY` (optional).
   - Place `voiceKey.json` (Google creds) in project root.
3. **Run**
   ```bash
   python main.py
   ```
4. **Operate**
   - **Voice Tab:** Say “arise” to activate, then speak commands.
   - **Mouse Tab:** Calibrate and use facial gestures to control the cursor.

## Built exe file:

<a href="https://drive.google.com/file/d/1PuLZ27Kegq4SD1PgZBKN520Y1cGrB5eX/view?usp=sharing">Download exe file</a>

## Contributors:

**Team Name:** CodeTasctic4

- Utsav Kasvala
- Pratik Nandan
- Vaibhav Kumar Maurya

### Made at:

<a href="https://hack36.com"> <img src="https://i.postimg.cc/FFwvfkGk/built-at-hack36.png" height="24px"> </a>
