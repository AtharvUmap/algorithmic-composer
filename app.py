import io
import json
import math
import struct
import tempfile
import time
import wave


import streamlit as st


try:
    import pretty_midi
except ImportError:
    pretty_midi = None




# ==========================================================
# The Algorithmic Composer — Health Edition
# Ticket 1: Real Music Generation + Downloadable MIDI
# ==========================================================


st.set_page_config(
    page_title="The Algorithmic Composer",
    page_icon="🎹",
    layout="centered",
)




# -----------------------------
# Visual Theme — animated gradient + glassmorphism + music UI
# -----------------------------
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&family=Nunito:wght@300;400;500;600&display=swap');

      /* === Animated gradient background === */
      @keyframes gradientShift {
          0%   { background-position:   0% 50%; }
          50%  { background-position: 100% 50%; }
          100% { background-position:   0% 50%; }
      }

      [data-testid="stAppViewContainer"] {
          background: linear-gradient(125deg, #d6c9ec 0%, #c9d8ec 35%, #ecc9dc 70%, #d6c9ec 100%);
          background-size: 280% 280%;
          animation: gradientShift 22s ease-in-out infinite;
          min-height: 100vh;
      }
      .main, .block-container {
          background: transparent !important;
          position: relative;
          z-index: 1;
      }

      /* === Base typography === */
      [data-testid="stAppViewContainer"] {
          font-family: 'Nunito', sans-serif;
          color: #2e3447;
      }
      h1, h2, h3, h4, h5, h6 {
          font-family: 'Quicksand', sans-serif !important;
          color: #4a3d6b;
          font-weight: 600;
          letter-spacing: 0.01em;
      }
      p, label, span, li {
          font-family: 'Nunito', sans-serif;
      }

      /* === Hero animation === */
      @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(14px); }
          to   { opacity: 1; transform: translateY(0); }
      }

      .main-title {
          text-align: center;
          font-family: 'Quicksand', sans-serif;
          font-size: 3rem;
          font-weight: 700;
          background: linear-gradient(135deg, #6e5a9b 0%, #5a7eb0 50%, #b06e9b 100%);
          -webkit-background-clip: text;
          background-clip: text;
          color: transparent;
          margin: 1rem 0 0.25rem 0;
          letter-spacing: 0.01em;
          animation: fadeInUp 0.8s ease-out;
      }
      .subtitle {
          text-align: center;
          font-family: 'Nunito', sans-serif;
          font-size: 1.2rem;
          color: #5a5e7a;
          font-style: italic;
          margin: 0 0 1rem 0;
          animation: fadeInUp 0.8s ease-out 0.15s backwards;
      }

      /* === Glassmorphism cards === */
      [data-testid="stVerticalBlockBorderWrapper"] {
          background: rgba(255, 255, 255, 0.22) !important;
          backdrop-filter: blur(14px) saturate(150%);
          -webkit-backdrop-filter: blur(14px) saturate(150%);
          border: 1px solid rgba(255, 255, 255, 0.32) !important;
          border-radius: 20px !important;
          box-shadow: 0 8px 28px rgba(70, 60, 110, 0.12);
          padding: 1.4rem !important;
      }

      /* === Glowing chord display === */
      @keyframes chordGlow {
          0%, 100% { text-shadow: 0 0 18px rgba(150, 130, 200, 0.5),  0 0 30px rgba(180, 140, 200, 0.25); }
          50%      { text-shadow: 0 0 28px rgba(150, 130, 200, 0.85), 0 0 42px rgba(180, 140, 200, 0.45); }
      }
      .chord-box {
          text-align: center;
          padding: 1.5rem 0;
          border-radius: 16px;
          background: rgba(255, 255, 255, 0.18);
          backdrop-filter: blur(8px);
          -webkit-backdrop-filter: blur(8px);
          border: 1px solid rgba(255, 255, 255, 0.3);
          margin: 0.5rem 0 0.75rem 0;
      }
      .chord-text {
          display: inline-block;
          font-family: 'Quicksand', sans-serif;
          font-size: 2.6rem;
          font-weight: 700;
          letter-spacing: 0.12em;
          background: linear-gradient(120deg, #6e5a9b 0%, #5a7eb0 50%, #b06e9b 100%);
          background-size: 200% 200%;
          -webkit-background-clip: text;
          background-clip: text;
          color: transparent;
          animation: chordGlow 3s ease-in-out infinite, gradientShift 8s ease-in-out infinite;
      }

      .mini-label {
          color: #5a5e7a;
          font-size: 0.9rem;
          margin-bottom: -0.4rem;
      }

      /* === Primary button === */
      .stButton > button {
          background: linear-gradient(135deg, #8e7fb8 0%, #a89bd0 100%);
          color: #ffffff !important;
          border: none !important;
          border-radius: 14px;
          padding: 0.75rem 1.5rem;
          font-family: 'Quicksand', sans-serif;
          font-weight: 600;
          letter-spacing: 0.02em;
          box-shadow: 0 4px 14px rgba(142, 127, 184, 0.4);
          transition: transform 120ms ease, box-shadow 120ms ease;
      }
      .stButton > button:hover {
          transform: translateY(-1px);
          box-shadow: 0 7px 20px rgba(142, 127, 184, 0.55);
      }
      .stButton > button:focus:not(:active) {
          color: #ffffff !important;
          border: none !important;
      }

      /* === Download button — warm peach contrast === */
      .stDownloadButton > button {
          background: linear-gradient(135deg, #d4a373 0%, #e8b98a 100%);
          color: #ffffff !important;
          border: none !important;
          border-radius: 14px;
          padding: 0.75rem 1.5rem;
          font-family: 'Quicksand', sans-serif;
          font-weight: 600;
          letter-spacing: 0.02em;
          box-shadow: 0 4px 14px rgba(212, 163, 115, 0.4);
          transition: transform 120ms ease, box-shadow 120ms ease;
      }
      .stDownloadButton > button:hover {
          transform: translateY(-1px);
          box-shadow: 0 7px 20px rgba(212, 163, 115, 0.55);
      }

      /* === Slider with mood-reactive glow === */
      .stSlider [role="slider"] {
          background-color: var(--mood-accent, #9b87cf) !important;
          border: 2px solid #ffffff !important;
          box-shadow:
              0 0 0 3px var(--mood-accent-soft, rgba(155, 135, 207, 0.25)),
              0 0 14px var(--mood-accent-glow, rgba(155, 135, 207, 0.55));
          transition: box-shadow 200ms ease, background-color 200ms ease;
      }
      .stSlider [role="slider"]:hover {
          box-shadow:
              0 0 0 4px var(--mood-accent-soft, rgba(155, 135, 207, 0.35)),
              0 0 22px var(--mood-accent-glow, rgba(155, 135, 207, 0.75));
      }

      /* === Alerts === */
      [data-testid="stAlert"] {
          border-radius: 14px;
          border: none !important;
          background: rgba(255, 255, 255, 0.3) !important;
          backdrop-filter: blur(8px);
      }
      [data-testid="stAlert"] * {
          color: #2e3447;
      }

      /* === Metric === */
      [data-testid="stMetric"] {
          background: rgba(255, 255, 255, 0.25);
          backdrop-filter: blur(8px);
          border-radius: 14px;
          border: 1px solid rgba(255, 255, 255, 0.3);
          padding: 0.8rem 1rem;
      }
      [data-testid="stMetricValue"] {
          color: #4a3d6b;
          font-family: 'Quicksand', sans-serif;
          font-weight: 600;
          font-size: clamp(0.95rem, 2.6vw, 1.55rem) !important;
          line-height: 1.2 !important;
          overflow: visible !important;
          text-overflow: clip !important;
          white-space: nowrap;
      }
      [data-testid="stMetricValue"] > div,
      [data-testid="stMetricValue"] * {
          overflow: visible !important;
          text-overflow: clip !important;
      }
      [data-testid="stMetricLabel"] {
          color: #6a637a;
      }

      /* === Divider === */
      hr { border-color: rgba(110, 90, 155, 0.18) !important; }

      /* === Expander === */
      [data-testid="stExpander"] {
          background: rgba(255, 255, 255, 0.25);
          backdrop-filter: blur(8px);
          border-radius: 14px;
          border: 1px solid rgba(255, 255, 255, 0.3);
      }
      [data-testid="stExpander"] summary {
          font-family: 'Quicksand', sans-serif;
          color: #4a3d6b;
      }

      /* === Selectbox base === */
      [data-baseweb="select"] > div {
          background: rgba(255, 255, 255, 0.55) !important;
          backdrop-filter: blur(8px);
          border-radius: 10px !important;
          border-color: rgba(110, 90, 155, 0.22) !important;
      }

      /* === Audio player === */
      audio { border-radius: 12px; width: 100%; }

      /* === Floating musical notes overlay === */
      .floating-notes {
          position: fixed;
          inset: 0;
          pointer-events: none;
          z-index: 0;
          overflow: hidden;
      }
      .floating-notes span {
          position: absolute;
          bottom: -60px;
          font-size: 1.6rem;
          color: rgba(110, 90, 155, 0.18);
          animation-name: floatUp;
          animation-iteration-count: infinite;
          animation-timing-function: linear;
          user-select: none;
      }
      @keyframes floatUp {
          0%   { transform: translate(0, 0) rotate(0deg); opacity: 0; }
          10%  { opacity: 1; }
          90%  { opacity: 1; }
          100% { transform: translate(40px, -110vh) rotate(20deg); opacity: 0; }
      }

      /* === Equalizer / waveform bars === */
      .equalizer {
          display: flex;
          justify-content: center;
          align-items: flex-end;
          gap: 4px;
          height: 36px;
          margin: 0.75rem 0 0.25rem 0;
      }
      .equalizer span {
          width: 5px;
          height: 100%;
          background: linear-gradient(180deg, #b06e9b 0%, #6e5a9b 50%, #5a7eb0 100%);
          border-radius: 3px;
          transform-origin: bottom;
          animation: eqBeat 0.85s ease-in-out infinite;
      }
      .equalizer span:nth-child(1)  { animation-delay: 0.00s; }
      .equalizer span:nth-child(2)  { animation-delay: 0.12s; }
      .equalizer span:nth-child(3)  { animation-delay: 0.24s; }
      .equalizer span:nth-child(4)  { animation-delay: 0.06s; }
      .equalizer span:nth-child(5)  { animation-delay: 0.18s; }
      .equalizer span:nth-child(6)  { animation-delay: 0.30s; }
      .equalizer span:nth-child(7)  { animation-delay: 0.09s; }
      .equalizer span:nth-child(8)  { animation-delay: 0.21s; }
      .equalizer span:nth-child(9)  { animation-delay: 0.15s; }
      .equalizer span:nth-child(10) { animation-delay: 0.27s; }
      .equalizer span:nth-child(11) { animation-delay: 0.33s; }
      .equalizer span:nth-child(12) { animation-delay: 0.05s; }
      @keyframes eqBeat {
          0%, 100% { transform: scaleY(0.25); opacity: 0.7; }
          50%      { transform: scaleY(1);    opacity: 1;   }
      }

      /* === Composing animation message === */
      .composing-msg {
          text-align: center;
          font-size: 1.5rem;
          font-family: 'Quicksand', sans-serif;
          color: #6e5a9b;
          padding: 1.5rem;
          letter-spacing: 0.06em;
          animation: composeFade 0.55s ease-in-out;
      }
      @keyframes composeFade {
          0%   { opacity: 0; transform: translateY(6px); }
          50%  { opacity: 1; transform: translateY(0); }
          100% { opacity: 0.6; transform: translateY(0); }
      }

      /* === Text contrast hardening === */
      .stMarkdown, .stMarkdown p, .stMarkdown li { color: #2e3447; }
      .stMarkdown strong { color: #1a1d2e; }

      [data-testid="stCaptionContainer"],
      [data-testid="stCaptionContainer"] p,
      .stCaption, small {
          color: #5a5e7a !important;
      }

      [data-testid="stWidgetLabel"],
      [data-testid="stWidgetLabel"] p {
          color: #2e3447 !important;
          font-weight: 500;
      }

      /* Selectbox: closed-state selected value */
      [data-baseweb="select"] [class*="ValueContainer"],
      [data-baseweb="select"] [class*="ValueContainer"] *,
      [data-baseweb="select"] [class*="SingleValue"],
      [data-baseweb="select"] [class*="SingleValue"] *,
      [data-baseweb="select"] > div > div,
      [data-baseweb="select"] > div > div * {
          color: #1a1a1a !important;
          font-weight: 600;
      }

      /* Selectbox: dropdown options — muted by default */
      ul[role="listbox"] li,
      ul[role="listbox"] li *,
      [data-baseweb="popover"] li,
      [data-baseweb="menu"] li,
      [data-baseweb="popover"] li *,
      [data-baseweb="menu"] li * {
          color: #8a9aa2 !important;
          font-weight: 400;
      }

      /* Selectbox: hovered/highlighted option — black bold */
      ul[role="listbox"] li:hover,
      ul[role="listbox"] li:hover *,
      ul[role="listbox"] li[aria-selected="true"],
      ul[role="listbox"] li[aria-selected="true"] *,
      [data-baseweb="popover"] li:hover,
      [data-baseweb="popover"] li:hover *,
      [data-baseweb="menu"] li:hover,
      [data-baseweb="menu"] li:hover * {
          color: #111111 !important;
          font-weight: 600;
      }

      a, a:visited { color: #6e5a9b; }
      a:hover      { color: #4a3d6b; }

      code {
          color: #4a3d6b !important;
          background: rgba(110, 90, 155, 0.14) !important;
          padding: 0.08rem 0.4rem;
          border-radius: 6px;
          font-size: 0.92em;
      }

      .stSlider [data-baseweb="slider"] { color: #4a3d6b; }

      /* === Emotional profile bars === */
      .profile-row {
          display: grid;
          grid-template-columns: 110px 1fr 70px;
          gap: 12px;
          align-items: center;
          margin: 8px 0;
      }
      .profile-label {
          font-family: 'Quicksand', sans-serif;
          font-weight: 500;
          color: #4a3d6b;
          font-size: 0.95rem;
      }
      .profile-bar {
          height: 12px;
          background: rgba(255, 255, 255, 0.45);
          border-radius: 6px;
          overflow: hidden;
          border: 1px solid rgba(255, 255, 255, 0.4);
      }
      .profile-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--mood-accent, #9b87cf), rgba(255, 255, 255, 0.7));
          border-radius: 6px;
          transition: width 400ms ease;
          box-shadow: 0 0 10px var(--mood-accent-glow, rgba(155, 135, 207, 0.45));
      }
      .profile-value {
          text-align: right;
          font-family: 'Quicksand', sans-serif;
          font-weight: 600;
          color: #4a3d6b;
          font-size: 0.95rem;
      }
      .profile-mood {
          margin-top: 0.7rem;
          font-family: 'Quicksand', sans-serif;
          color: #4a3d6b;
      }
      .profile-mood strong {
          color: #1a1d2e;
      }

      /* === Music prescription list === */
      .prescription {
          font-family: 'Nunito', sans-serif;
          color: #2e3447;
          line-height: 1.8;
      }
      .prescription strong {
          color: #4a3d6b;
          font-family: 'Quicksand', sans-serif;
      }

      /* === Before → After transition arrow === */
      .transition-arrow {
          text-align: center;
          font-size: 2rem;
          color: var(--mood-accent, #6e5a9b);
          margin: 0.5rem 0 0.25rem 0;
          line-height: 1;
          text-shadow: 0 0 12px var(--mood-accent-glow, rgba(110, 90, 155, 0.4));
      }
      .stage-label {
          text-align: center;
          font-family: 'Quicksand', sans-serif;
          color: #4a3d6b;
          font-weight: 600;
          letter-spacing: 0.04em;
          margin: 0.4rem 0 0.6rem 0;
      }

      /* === Why-this-works bullets === */
      .why-list {
          font-family: 'Nunito', sans-serif;
          color: #2e3447;
          line-height: 1.8;
          padding-left: 1.1rem;
      }
      .why-list li {
          margin: 0.35rem 0;
      }
      .why-list strong {
          color: #4a3d6b;
          font-family: 'Quicksand', sans-serif;
      }
    </style>
    """,
    unsafe_allow_html=True,
)




# -----------------------------
# Session State Defaults
# -----------------------------
if "last_result" not in st.session_state:
    st.session_state.last_result = None




# -----------------------------
# Core Helpers
# -----------------------------
def clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(value, upper))




def get_intensity_label(stress: int, heart_rate: int) -> str:
    if stress >= 80 or heart_rate >= 105:
        return "High Regulation Need"
    if stress >= 55 or heart_rate >= 90:
        return "Moderate Regulation Need"
    return "Low Regulation Need"




# -----------------------------
# Deterministic Music Engine
# -----------------------------
def generate_therapeutic_music(stress: int, energy: int, heart_rate: int, mood: str) -> dict:
    mood_profiles = {
        "Stressed": {
            "key": "A minor resolving to C major",
            "progression": ["Am", "F", "C", "G"],
            "rhythm": "Slow, steady quarter-note pulse",
            "instruction": "Play each chord for four beats. Keep the left hand soft, even, and grounded.",
            "texture": "Warm sustained piano chords with minimal movement",
            "goal": "lower arousal and create a clear sense of resolution",
            "melody_shape": "descending",
        },
        "Anxious": {
            "key": "D minor resolving to F major",
            "progression": ["Dm", "Bb", "F", "C"],
            "rhythm": "Descending, calming pattern",
            "instruction": "Play slowly with a descending right-hand melody. Avoid sharp accents or sudden jumps.",
            "texture": "Gentle broken chords with predictable repetition",
            "goal": "reduce nervous momentum through repetition and downward motion",
            "melody_shape": "descending",
        },
        "Focused": {
            "key": "C major",
            "progression": ["C", "G", "Am", "F"],
            "rhythm": "Minimal repeating eighth-note pattern",
            "instruction": "Repeat the progression evenly to create a stable focus loop. Keep dynamics consistent.",
            "texture": "Clean pulse with light right-hand repetition",
            "goal": "support concentration through structure, predictability, and moderate energy",
            "melody_shape": "arpeggio",
        },
        "Calm": {
            "key": "C major",
            "progression": ["C", "F", "G", "C"],
            "rhythm": "Gentle open chords with space between changes",
            "instruction": "Use spacious chords and let each harmony ring before moving to the next one.",
            "texture": "Open voicings, soft pedal, and long rests",
            "goal": "maintain relaxation with consonant harmony and low musical density",
            "melody_shape": "open",
        },
        "Tired": {
            "key": "G major",
            "progression": ["G", "D", "Em", "C"],
            "rhythm": "Light uplifting pulse",
            "instruction": "Play softly but slightly brighter. Keep the rhythm gentle, not aggressive.",
            "texture": "Simple major-key pulse with modest lift",
            "goal": "increase alertness without overstimulation",
            "melody_shape": "rising",
        },
    }


    profile = mood_profiles[mood]


    headline_goals = {
        "Stressed": "Lower arousal",
        "Anxious":  "Ease nervous momentum",
        "Focused":  "Sustain concentration",
        "Calm":     "Maintain relaxation",
        "Tired":    "Lift energy gently",
    }


    tempo = 90
    tempo -= stress // 4
    tempo -= max(0, heart_rate - 80) // 5
    tempo += energy // 10


    if mood in ["Stressed", "Anxious"]:
        tempo -= 5
    elif mood == "Focused":
        tempo += 4
    elif mood == "Tired":
        tempo += 6


    tempo = clamp(tempo, 55, 110)


    if stress >= 75 or heart_rate >= 100:
        performance_density = "Low density: one chord per measure, no sudden accents"
        loop_count = 2
        beats_per_chord = 4
    elif energy >= 70 and mood == "Focused":
        performance_density = "Medium density: steady repeated pattern with light motion"
        loop_count = 3
        beats_per_chord = 2
    else:
        performance_density = "Gentle density: relaxed chord changes with room to breathe"
        loop_count = 2
        beats_per_chord = 4


    explanation = (
        f"Because the selected state is **{mood}**, with stress at **{stress}/100** "
        f"and heart rate at **{heart_rate} BPM**, this profile uses a controlled tempo of "
        f"**{tempo} BPM** and a predictable harmonic loop. The goal is to {profile['goal']}. "
        f"The progression {' → '.join(profile['progression'])} is simple enough to perform live, "
        f"while the rhythm stays stable so the listener can settle into the pattern."
    )


    return {
        "tempo": tempo,
        "key": profile["key"],
        "progression": profile["progression"],
        "rhythm": profile["rhythm"],
        "instruction": profile["instruction"],
        "texture": profile["texture"],
        "performance_density": performance_density,
        "loop_count": loop_count,
        "beats_per_chord": beats_per_chord,
        "melody_shape": profile["melody_shape"],
        "intensity_label": get_intensity_label(stress, heart_rate),
        "goal": profile["goal"],
        "headline_goal": headline_goals[mood],
        "explanation": explanation,
    }




# -----------------------------
# Music Theory Mappings
# -----------------------------
NOTE_FREQUENCIES = {
    "C2": 65.41,
    "D2": 73.42,
    "E2": 82.41,
    "F2": 87.31,
    "G2": 98.00,
    "A2": 110.00,
    "Bb2": 116.54,
    "B2": 123.47,
    "C3": 130.81,
    "D3": 146.83,
    "E3": 164.81,
    "F3": 174.61,
    "G3": 196.00,
    "A3": 220.00,
    "Bb3": 233.08,
    "B3": 246.94,
    "C4": 261.63,
    "D4": 293.66,
    "E4": 329.63,
    "F4": 349.23,
    "G4": 392.00,
    "A4": 440.00,
    "Bb4": 466.16,
    "B4": 493.88,
    "C5": 523.25,
    "D5": 587.33,
    "E5": 659.25,
}


NOTE_MIDI = {
    "C2": 36,
    "D2": 38,
    "E2": 40,
    "F2": 41,
    "G2": 43,
    "A2": 45,
    "Bb2": 46,
    "B2": 47,
    "C3": 48,
    "D3": 50,
    "E3": 52,
    "F3": 53,
    "G3": 55,
    "A3": 57,
    "Bb3": 58,
    "B3": 59,
    "C4": 60,
    "D4": 62,
    "E4": 64,
    "F4": 65,
    "G4": 67,
    "A4": 69,
    "Bb4": 70,
    "B4": 71,
    "C5": 72,
    "D5": 74,
    "E5": 76,
}


CHORD_NOTES = {
    "C": ["C4", "E4", "G4"],
    "D": ["D4", "F4", "A4"],
    "Dm": ["D4", "F4", "A4"],
    "Em": ["E4", "G4", "B4"],
    "F": ["F3", "A3", "C4"],
    "G": ["G3", "B3", "D4"],
    "Am": ["A3", "C4", "E4"],
    "Bb": ["Bb3", "D4", "F4"],
}


BASS_NOTES = {
    "C": "C2",
    "D": "D2",
    "Dm": "D2",
    "Em": "E2",
    "F": "F2",
    "G": "G2",
    "Am": "A2",
    "Bb": "Bb2",
}




# -----------------------------
# Browser Audio Preview Generator
# -----------------------------
def apply_envelope(sample: float, sample_index: int, total_samples: int, sample_rate: int) -> float:
    attack_samples = int(sample_rate * 0.025)
    release_samples = int(sample_rate * 0.22)


    if sample_index < attack_samples:
        return sample * (sample_index / max(1, attack_samples))


    if sample_index > total_samples - release_samples:
        remaining = total_samples - sample_index
        return sample * (remaining / max(1, release_samples))


    return sample




def note_wave(note: str, t: float) -> float:
    freq = NOTE_FREQUENCIES[note]
    return (
        math.sin(2 * math.pi * freq * t)
        + 0.25 * math.sin(2 * math.pi * freq * 2 * t)
        + 0.08 * math.sin(2 * math.pi * freq * 3 * t)
    )




def chord_to_samples(chord: str, duration: float, sample_rate: int, volume: float) -> list[int]:
    notes = CHORD_NOTES.get(chord, CHORD_NOTES["C"])
    bass_note = BASS_NOTES.get(chord, "C2")
    total_samples = int(duration * sample_rate)
    samples = []


    for i in range(total_samples):
        t = i / sample_rate
        value = 0.0


        # Soft left-hand bass foundation.
        value += 0.55 * note_wave(bass_note, t)


        # Right-hand chord.
        for note in notes:
            value += note_wave(note, t) / len(notes)


        value /= 1.7
        value = apply_envelope(value, i, total_samples, sample_rate)
        samples.append(int(32767 * volume * value))


    return samples




def melody_note_sequence(chord: str, shape: str) -> list[str]:
    notes = CHORD_NOTES.get(chord, CHORD_NOTES["C"])


    if shape == "descending":
        return [notes[2], notes[1], notes[0], notes[1]]
    if shape == "rising":
        return [notes[0], notes[1], notes[2], notes[2]]
    if shape == "open":
        return [notes[0], notes[2], notes[1], notes[2]]
    return [notes[0], notes[1], notes[2], notes[1]]




def generate_piano_wav(
    progression: list[str],
    tempo: int,
    beats_per_chord: int = 4,
    loops: int = 2,
    melody_shape: str = "arpeggio",
) -> bytes:
    sample_rate = 44_100
    seconds_per_beat = 60 / tempo
    chord_duration = seconds_per_beat * beats_per_chord
    volume = 0.22


    all_samples = []
    melody_volume = 0.12


    for _ in range(loops):
        for chord in progression:
            chord_samples = chord_to_samples(chord, chord_duration, sample_rate, volume)
            melody_notes = melody_note_sequence(chord, melody_shape)
            note_duration = chord_duration / len(melody_notes)


            melody_samples = [0] * len(chord_samples)
            cursor = 0
            for melody_note in melody_notes:
                total_note_samples = int(note_duration * sample_rate)
                for i in range(total_note_samples):
                    if cursor + i >= len(melody_samples):
                        break
                    t = i / sample_rate
                    raw = note_wave(melody_note, t)
                    shaped = apply_envelope(raw, i, total_note_samples, sample_rate)
                    melody_samples[cursor + i] += int(32767 * melody_volume * shaped)
                cursor += total_note_samples


            combined = []
            for chord_sample, melody_sample in zip(chord_samples, melody_samples):
                combined.append(clamp(chord_sample + melody_sample, -32767, 32767))


            all_samples.extend(combined)


    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack(f"<{len(all_samples)}h", *all_samples))


    return buffer.getvalue()




# -----------------------------
# MIDI Generator
# -----------------------------
def add_midi_note(instrument, note_name: str, start: float, end: float, velocity: int) -> None:
    if pretty_midi is None:
        return


    pitch = NOTE_MIDI[note_name]
    note = pretty_midi.Note(
        velocity=velocity,
        pitch=pitch,
        start=start,
        end=end,
    )
    instrument.notes.append(note)




def generate_midi_bytes(
    progression: list[str],
    tempo: int,
    beats_per_chord: int = 4,
    loops: int = 2,
    melody_shape: str = "arpeggio",
) -> bytes:
    if pretty_midi is None:
        raise RuntimeError("pretty_midi is not installed. Run: pip install pretty_midi")


    midi = pretty_midi.PrettyMIDI(initial_tempo=tempo)
    piano = pretty_midi.Instrument(program=0, name="Therapeutic Piano")


    seconds_per_beat = 60 / tempo
    chord_duration = seconds_per_beat * beats_per_chord
    current_time = 0.0


    for _ in range(loops):
        for chord in progression:
            chord_notes = CHORD_NOTES.get(chord, CHORD_NOTES["C"])
            bass_note = BASS_NOTES.get(chord, "C2")


            # Left hand: sustained bass note.
            add_midi_note(
                piano,
                bass_note,
                current_time,
                current_time + chord_duration * 0.92,
                velocity=58,
            )


            # Right hand: sustained chord voicing.
            for note_name in chord_notes:
                add_midi_note(
                    piano,
                    note_name,
                    current_time,
                    current_time + chord_duration * 0.88,
                    velocity=66,
                )


            # Right hand: light melodic movement above the chord.
            melody_notes = melody_note_sequence(chord, melody_shape)
            melody_step = chord_duration / len(melody_notes)
            for index, note_name in enumerate(melody_notes):
                start = current_time + index * melody_step
                end = start + melody_step * 0.72
                add_midi_note(piano, note_name, start, end, velocity=78)


            current_time += chord_duration


    midi.instruments.append(piano)


    with tempfile.NamedTemporaryFile(suffix=".mid") as temp_file:
        midi.write(temp_file.name)
        temp_file.seek(0)
        return temp_file.read()




# -----------------------------
# Interactive Piano Keyboard (HTML + CSS + Web Audio)
# -----------------------------
PIANO_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@500;600&display=swap');

  html, body {
    margin: 0;
    padding: 0;
    background: transparent;
    font-family: 'Quicksand', sans-serif;
  }

  .piano-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px 0 22px 0;
  }

  .chord-bar {
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
    padding-top: 24px;
    margin-bottom: 14px;
    max-width: 560px;
  }

  .chord-btn {
    position: relative;
    background: linear-gradient(135deg, #7ba098 0%, #8fb5a9 100%);
    color: #ffffff;
    border: none;
    border-radius: 12px;
    padding: 0.55rem 1.1rem;
    font-family: 'Quicksand', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    letter-spacing: 0.02em;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(123, 160, 152, 0.32);
    transition: transform 100ms ease, box-shadow 100ms ease, background 200ms ease;
  }

  .chord-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(123, 160, 152, 0.42);
  }

  /* The chord the player should hit next — peach gradient, pulsing glow, arrow above */
  .chord-btn.next {
    background: linear-gradient(135deg, #d4a373 0%, #e8b98a 100%);
    box-shadow: 0 3px 14px rgba(212, 163, 115, 0.55);
    animation: nextPulse 1.3s ease-in-out infinite;
  }

  .chord-btn.next::before {
    content: "▼";
    position: absolute;
    top: -22px;
    left: 50%;
    transform: translateX(-50%);
    color: #c98a55;
    font-size: 1rem;
    text-shadow: 0 1px 2px rgba(255, 255, 255, 0.6);
    animation: nextArrowBob 1.3s ease-in-out infinite;
  }

  @keyframes nextPulse {
    0%, 100% { box-shadow: 0 3px 14px rgba(212, 163, 115, 0.45); }
    50%      { box-shadow: 0 3px 22px rgba(212, 163, 115, 0.85); }
  }

  @keyframes nextArrowBob {
    0%, 100% { transform: translate(-50%, 0); }
    50%      { transform: translate(-50%, 4px); }
  }

  .piano {
    position: relative;
    display: flex;
    width: 100%;
    max-width: 560px;
    height: 200px;
    box-sizing: border-box;
    background: linear-gradient(180deg, #2a2a2a 0%, #161616 100%);
    padding: 14px 12px 18px 12px;
    border-radius: 14px;
    box-shadow:
      0 10px 28px rgba(50, 60, 65, 0.28),
      inset 0 -3px 6px rgba(0, 0, 0, 0.45),
      inset 0 1px 0 rgba(255, 255, 255, 0.05);
  }

  .white-keys {
    display: flex;
    gap: 2px;
    width: 100%;
    height: 100%;
  }

  .white-key {
    flex: 1;
    background: linear-gradient(180deg, #fdfcf6 0%, #f1ecda 100%);
    border-radius: 0 0 6px 6px;
    box-shadow:
      0 3px 0 rgba(0, 0, 0, 0.2),
      inset 0 -5px 8px rgba(60, 50, 30, 0.06);
    cursor: pointer;
    position: relative;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding-bottom: 10px;
    color: #6a7378;
    font-size: 0.78rem;
    font-weight: 600;
    user-select: none;
    -webkit-user-select: none;
    transition: transform 70ms ease, background 70ms ease, box-shadow 70ms ease;
  }

  .white-key.pressed {
    transform: translateY(2px);
    background: linear-gradient(180deg, #ece6d2 0%, #d6cfb8 100%);
    box-shadow:
      0 1px 0 rgba(0, 0, 0, 0.25),
      inset 0 -3px 6px rgba(0, 0, 0, 0.08);
  }

  .white-key.highlighted {
    background: linear-gradient(180deg, #b9d4cd 0%, #8fb5a9 100%);
    color: #ffffff;
    box-shadow:
      0 3px 0 rgba(123, 160, 152, 0.4),
      inset 0 -3px 6px rgba(74, 104, 99, 0.12);
  }

  .black-keys {
    position: absolute;
    top: 14px;
    left: 12px;
    right: 12px;
    height: 118px;
    pointer-events: none;
  }

  .black-key {
    position: absolute;
    width: 9%;
    height: 100%;
    background: linear-gradient(180deg, #2c2c2c 0%, #060606 100%);
    border-radius: 0 0 5px 5px;
    box-shadow:
      0 3px 0 rgba(0, 0, 0, 0.55),
      inset 0 -3px 4px rgba(255, 255, 255, 0.06),
      inset 0 1px 0 rgba(255, 255, 255, 0.08);
    cursor: pointer;
    pointer-events: auto;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding-bottom: 8px;
    color: #c8d0d4;
    font-size: 0.7rem;
    font-weight: 600;
    user-select: none;
    -webkit-user-select: none;
    transition: transform 70ms ease, background 70ms ease, box-shadow 70ms ease;
    z-index: 2;
  }

  .black-key.pressed {
    transform: translateY(2px);
    background: linear-gradient(180deg, #181818 0%, #050505 100%);
    box-shadow: 0 1px 0 rgba(0, 0, 0, 0.55);
  }

  .black-key.highlighted {
    background: linear-gradient(180deg, #5a7872 0%, #3d5651 100%);
    color: #ffffff;
    box-shadow: 0 3px 0 rgba(74, 104, 99, 0.55);
  }
</style>
</head>
<body>
<div class="piano-wrap">
  <div class="chord-bar" id="chordBar"></div>
  <div class="piano">
    <div class="white-keys">
      <div class="white-key" data-note="C4"  data-freq="261.63">C</div>
      <div class="white-key" data-note="D4"  data-freq="293.66">D</div>
      <div class="white-key" data-note="E4"  data-freq="329.63">E</div>
      <div class="white-key" data-note="F4"  data-freq="349.23">F</div>
      <div class="white-key" data-note="G4"  data-freq="392.00">G</div>
      <div class="white-key" data-note="A4"  data-freq="440.00">A</div>
      <div class="white-key" data-note="B4"  data-freq="493.88">B</div>
    </div>
    <div class="black-keys">
      <div class="black-key" data-note="C#4" data-freq="277.18" style="left: 9.65%;">C#</div>
      <div class="black-key" data-note="D#4" data-freq="311.13" style="left: 23.99%;">D#</div>
      <div class="black-key" data-note="F#4" data-freq="369.99" style="left: 52.67%;">F#</div>
      <div class="black-key" data-note="G#4" data-freq="415.30" style="left: 67.01%;">G#</div>
      <div class="black-key" data-note="A#4" data-freq="466.16" style="left: 81.35%;">A#</div>
    </div>
  </div>
</div>
<script>
  // Injected from Python
  const PROGRESSION = __PROGRESSION_JSON__;
  const TEMPO = __TEMPO__;
  const BEATS_PER_CHORD = __BEATS_PER_CHORD__;
  const CHORD_DURATION_MS = (60 / TEMPO) * BEATS_PER_CHORD * 1000;

  // Note frequencies (octave 4)
  const NOTE_FREQ = {
    "C":  261.63, "C#": 277.18,
    "D":  293.66, "D#": 311.13,
    "E":  329.63,
    "F":  349.23, "F#": 369.99,
    "G":  392.00, "G#": 415.30,
    "A":  440.00, "A#": 466.16,
    "B":  493.88
  };

  // Chord symbol → constituent notes (octave-agnostic)
  const CHORDS = {
    "C":  ["C", "E", "G"],
    "D":  ["D", "F#", "A"],
    "Dm": ["D", "F", "A"],
    "Em": ["E", "G", "B"],
    "F":  ["F", "A", "C"],
    "G":  ["G", "B", "D"],
    "Am": ["A", "C", "E"],
    "Bb": ["A#", "D", "F"]
  };

  let audioCtx = null;
  function ensureCtx() {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
  }

  function playNote(freq, duration, peakGain) {
    ensureCtx();
    const dur = duration || 1.1;
    const peak = peakGain || 0.32;
    const now = audioCtx.currentTime;

    const master = audioCtx.createGain();
    master.connect(audioCtx.destination);
    master.gain.setValueAtTime(0, now);
    master.gain.linearRampToValueAtTime(peak, now + 0.012);
    master.gain.exponentialRampToValueAtTime(0.0008, now + dur);

    const harmonics = [
      { mult: 1, level: 1.00 },
      { mult: 2, level: 0.45 },
      { mult: 3, level: 0.22 },
      { mult: 4, level: 0.10 }
    ];
    harmonics.forEach((h) => {
      const osc = audioCtx.createOscillator();
      const g = audioCtx.createGain();
      g.gain.value = h.level;
      osc.type = 'sine';
      osc.frequency.value = freq * h.mult;
      osc.connect(g).connect(master);
      osc.start(now);
      osc.stop(now + dur);
    });
  }

  function highlightKey(note, durationMs) {
    const el = document.querySelector('[data-note="' + note + '4"]');
    if (!el) return;
    el.classList.add('highlighted');
    setTimeout(function () { el.classList.remove('highlighted'); }, durationMs || 500);
  }

  function pressKey(el) {
    el.classList.add('pressed');
    setTimeout(function () { el.classList.remove('pressed'); }, 150);
    const freq = parseFloat(el.dataset.freq);
    playNote(freq);
  }

  function playChord(chord, opts) {
    const notes = CHORDS[chord];
    if (!notes) return;
    const noteDuration = (opts && opts.noteDuration) || 1.4;
    const highlightMs = (opts && opts.highlightMs) || 500;
    // Lower per-voice gain since 3 notes stack
    const peakGain = 0.18;
    notes.forEach((note) => {
      const freq = NOTE_FREQ[note];
      if (!freq) return;
      playNote(freq, noteDuration, peakGain);
      highlightKey(note, highlightMs);
    });
  }

  // Build chord buttons. The "next chord to hit" is highlighted; clicking
  // any chord plays it and advances the highlight to the following chord
  // (wrapping at the end of the progression).
  const bar = document.getElementById('chordBar');
  const chordButtons = [];

  function setNext(index) {
    chordButtons.forEach((b, i) => b.classList.toggle('next', i === index));
  }

  PROGRESSION.forEach((chord, index) => {
    const btn = document.createElement('button');
    btn.className = 'chord-btn';
    btn.textContent = chord;
    btn.addEventListener('click', () => {
      playChord(chord);
      if (PROGRESSION.length > 0) {
        setNext((index + 1) % PROGRESSION.length);
      }
    });
    bar.appendChild(btn);
    chordButtons.push(btn);
  });

  if (chordButtons.length > 0) {
    setNext(0);
  }

  // Single-key click handlers
  document.querySelectorAll('.white-key, .black-key').forEach((key) => {
    key.addEventListener('mousedown', (e) => {
      e.preventDefault();
      pressKey(key);
    });
    key.addEventListener('touchstart', (e) => {
      e.preventDefault();
      pressKey(key);
    }, { passive: false });
  });
</script>
</body>
</html>
"""


def render_piano_html(progression: list[str], tempo: int = 75, beats_per_chord: int = 4) -> str:
    """Inject the chord progression + timing into the piano template as JSON."""
    return (
        PIANO_HTML_TEMPLATE
        .replace("__PROGRESSION_JSON__", json.dumps(progression))
        .replace("__TEMPO__", str(int(tempo)))
        .replace("__BEATS_PER_CHORD__", str(int(beats_per_chord)))
    )


# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="main-title">🎹 The Algorithmic Composer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Transform your mental state into therapeutic music.</div>',
    unsafe_allow_html=True,
)


# Background overlay — floating musical notes
st.markdown(
    """
    <div class="floating-notes">
      <span style="left:  5%; animation-duration: 22s; animation-delay:  0s;">♪</span>
      <span style="left: 14%; animation-duration: 28s; animation-delay:  4s;">♫</span>
      <span style="left: 23%; animation-duration: 26s; animation-delay:  9s;">♬</span>
      <span style="left: 34%; animation-duration: 30s; animation-delay:  2s;">♩</span>
      <span style="left: 44%; animation-duration: 24s; animation-delay: 11s;">♪</span>
      <span style="left: 54%; animation-duration: 27s; animation-delay:  6s;">♫</span>
      <span style="left: 64%; animation-duration: 29s; animation-delay:  1s;">♬</span>
      <span style="left: 74%; animation-duration: 25s; animation-delay:  8s;">♪</span>
      <span style="left: 84%; animation-duration: 31s; animation-delay: 14s;">♩</span>
      <span style="left: 92%; animation-duration: 23s; animation-delay:  5s;">♫</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Input Controls
# -----------------------------
st.subheader("How are you feeling right now?")


with st.container(border=True):
    stress = st.slider("Stress Level", 0, 100, 70)
    energy = st.slider("Energy Level", 0, 100, 40)
    heart_rate = st.slider("Heart Rate", 40, 160, 90)
    mood = st.selectbox(
        "Current State",
        ["Stressed", "Anxious", "Focused", "Calm", "Tired"],
    )


# Mood-reactive accent (Stressed→purple, Anxious→amber, Focused→teal, Calm→blue, Tired→orange)
MOOD_ACCENTS = {
    "Stressed": ("#a584c4", "165, 132, 196"),
    "Anxious":  ("#d8a04e", "216, 160,  78"),
    "Focused":  ("#5fa39a", " 95, 163, 154"),
    "Calm":     ("#5d8cb8", " 93, 140, 184"),
    "Tired":    ("#e09b6e", "224, 155, 110"),
}
_accent_hex, _accent_rgb = MOOD_ACCENTS.get(mood, ("#9b87cf", "155, 135, 207"))
st.markdown(
    f"""
    <style>
      :root {{
        --mood-accent: {_accent_hex};
        --mood-accent-soft: rgba({_accent_rgb}, 0.25);
        --mood-accent-glow: rgba({_accent_rgb}, 0.60);
      }}
    </style>
    """,
    unsafe_allow_html=True,
)


col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("Stress", f"{stress}/100")
col_b.metric("Energy", f"{energy}/100")
col_c.metric("Heart Rate", f"{heart_rate} BPM")
col_d.metric("Mood", mood)


st.divider()




# -----------------------------
# Generate Results
# -----------------------------
compose_button = st.button("Generate Therapeutic Music", use_container_width=True, type="primary")


if compose_button:
    _compose_placeholder = st.empty()
    for _msg in ("♪ composing harmony ♪", "♪ shaping rhythm ♪", "♪ resolving tension ♪"):
        _compose_placeholder.markdown(
            f'<div class="composing-msg">{_msg}</div>',
            unsafe_allow_html=True,
        )
        time.sleep(0.55)
    _compose_placeholder.empty()
    st.session_state.last_result = generate_therapeutic_music(stress, energy, heart_rate, mood)


if st.session_state.last_result:
    result = st.session_state.last_result
    progression_text = " → ".join(result["progression"])


    metric_col_1, metric_col_2 = st.columns(2)
    metric_col_1.metric("Recommended Tempo", f"{result['tempo']} BPM")
    metric_col_2.metric("Regulation Profile", result["intensity_label"])


    # Emotional Profile + Music Prescription
    with st.container(border=True):
        prof_col, rx_col = st.columns([3, 2])

        with prof_col:
            st.markdown("**Emotional Profile**")
            stress_pct = stress
            energy_pct = energy
            hr_pct = max(0, min(100, round((heart_rate - 40) / 1.2)))
            st.markdown(
                f"""
                <div class="profile-row">
                  <span class="profile-label">Stress</span>
                  <div class="profile-bar"><div class="profile-fill" style="width: {stress_pct}%;"></div></div>
                  <span class="profile-value">{stress}</span>
                </div>
                <div class="profile-row">
                  <span class="profile-label">Energy</span>
                  <div class="profile-bar"><div class="profile-fill" style="width: {energy_pct}%;"></div></div>
                  <span class="profile-value">{energy}</span>
                </div>
                <div class="profile-row">
                  <span class="profile-label">Heart Rate</span>
                  <div class="profile-bar"><div class="profile-fill" style="width: {hr_pct}%;"></div></div>
                  <span class="profile-value">{heart_rate} BPM</span>
                </div>
                <div class="profile-mood"><strong>Mood:</strong> {mood}</div>
                """,
                unsafe_allow_html=True,
            )

        with rx_col:
            st.markdown("**Music Prescription**")
            st.markdown(
                f"""
                <div class="prescription">
                  <strong>Tempo:</strong> {result['tempo']} BPM<br>
                  <strong>Key:</strong> {result['key']}<br>
                  <strong>Pattern:</strong> {result['melody_shape'].title()}<br>
                  <strong>Goal:</strong> {result['headline_goal']}
                </div>
                """,
                unsafe_allow_html=True,
            )


    # Before → After Prediction
    predicted_stress = max(20, stress - 25)
    predicted_energy = min(80, energy + 10)
    predicted_hr = max(60, heart_rate - 18)

    with st.container(border=True):
        st.subheader("📈 Predicted Effect")
        st.caption("Estimated emotional state after one full listen of the generated piece.")

        st.markdown('<div class="stage-label">Current State</div>', unsafe_allow_html=True)
        cur_a, cur_b, cur_c = st.columns(3)
        cur_a.metric("Stress", stress)
        cur_b.metric("Energy", energy)
        cur_c.metric("Heart Rate", f"{heart_rate} BPM")

        st.markdown('<div class="transition-arrow">↓</div>', unsafe_allow_html=True)

        st.markdown('<div class="stage-label">After Listening (Predicted)</div>', unsafe_allow_html=True)
        post_a, post_b, post_c = st.columns(3)
        post_a.metric(
            "Stress",
            predicted_stress,
            delta=predicted_stress - stress,
            delta_color="inverse",
        )
        post_b.metric(
            "Energy",
            predicted_energy,
            delta=predicted_energy - energy,
        )
        post_c.metric(
            "Heart Rate",
            f"{predicted_hr} BPM",
            delta=f"{predicted_hr - heart_rate} BPM",
            delta_color="inverse",
        )


    with st.container(border=True):
        st.subheader("🎼 Composition Profile")

        st.markdown("**Chord Progression**")
        st.markdown(
            f'<div class="chord-box"><span class="chord-text">{progression_text}</span></div>',
            unsafe_allow_html=True,
        )


        st.markdown(f"**Rhythm Feel:** {result['rhythm']}")
        st.markdown(f"**Texture:** {result['texture']}")
        st.markdown(f"**Performance Density:** {result['performance_density']}")
        st.markdown(f"**Melody Shape:** {result['melody_shape'].title()}")


    with st.container(border=True):
        st.subheader("🎹 Interactive Keyboard")
        st.caption(
            "Follow the pulsing chord button (▼) to walk through your "
            "progression — each click plays the chord, lights up the keys, "
            "and points to the next chord to play."
        )
        st.components.v1.html(
            render_piano_html(
                result["progression"],
                result["tempo"],
                result["beats_per_chord"],
            ),
            height=350,
        )


    with st.container(border=True):
        st.subheader("🔊 Hear the Generated Piano Arrangement")


        audio_bytes = generate_piano_wav(
            progression=result["progression"],
            tempo=result["tempo"],
            beats_per_chord=result["beats_per_chord"],
            loops=result["loop_count"],
            melody_shape=result["melody_shape"],
        )
        st.audio(audio_bytes, format="audio/wav")
        st.markdown(
            """
            <div class="equalizer">
              <span></span><span></span><span></span><span></span>
              <span></span><span></span><span></span><span></span>
              <span></span><span></span><span></span><span></span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Generated locally with left-hand bass, right-hand chords, and a simple melody layer.")


        if pretty_midi is not None:
            try:
                midi_bytes = generate_midi_bytes(
                    progression=result["progression"],
                    tempo=result["tempo"],
                    beats_per_chord=result["beats_per_chord"],
                    loops=result["loop_count"],
                    melody_shape=result["melody_shape"],
                )
                st.download_button(
                    label="Download MIDI File",
                    data=midi_bytes,
                    file_name="therapeutic_composition.mid",
                    mime="audio/midi",
                    use_container_width=True,
                )
            except Exception as error:
                st.warning(f"MIDI generation failed: {error}")
        else:
            st.info("Install pretty_midi to enable downloadable MIDI: `pip install pretty_midi`")


    with st.container(border=True):
        st.subheader("🧠 Why This Music Works")

        why_bullets = []

        if result["tempo"] < 75:
            why_bullets.append(
                f"<strong>Slow tempo ({result['tempo']} BPM)</strong> reduces physiological arousal"
            )
        elif result["tempo"] > 90:
            why_bullets.append(
                f"<strong>Brighter tempo ({result['tempo']} BPM)</strong> gently lifts energy without overstimulation"
            )
        else:
            why_bullets.append(
                f"<strong>Steady tempo ({result['tempo']} BPM)</strong> stabilizes the nervous system"
            )

        shape_descriptions = {
            "descending": "<strong>Descending melody</strong> encourages mental relaxation",
            "rising":     "<strong>Rising melody</strong> invites gentle activation",
            "open":       "<strong>Open voicings</strong> create space and breathing room",
            "arpeggio":   "<strong>Repeated arpeggios</strong> support sustained attention",
        }
        why_bullets.append(
            shape_descriptions.get(
                result["melody_shape"],
                f"<strong>{result['melody_shape'].title()} pattern</strong> structures the listening experience",
            )
        )

        if "resolving" in result["key"].lower():
            why_bullets.append(
                f"<strong>Minor → major resolution</strong> in {result['key']} releases harmonic tension"
            )
        else:
            why_bullets.append(
                f"<strong>{result['key']}</strong> provides consonant, stable harmony"
            )

        why_bullets.append(
            "<strong>Predictable repetition</strong> — familiarity itself is regulating for the nervous system"
        )

        bullets_html = "".join(f"<li>{b}</li>" for b in why_bullets)
        st.markdown(f'<ul class="why-list">{bullets_html}</ul>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(result["explanation"])






# -----------------------------
# Footer Disclaimer
# -----------------------------
st.divider()
st.caption(
    "**Health Track Prototype.** This app converts stress, energy, heart rate, and mood "
    "into structured piano music for relaxation, focus, or emotional regulation. It "
    "generates piano audio with left-hand bass, right-hand chords, and a simple melody, "
    "and exports a downloadable MIDI file for live performance or DAW playback."
)
st.caption(
    "This prototype is for wellness and creative exploration only. It is not medical advice, "
    "a diagnosis tool, or a replacement for care from a qualified health professional."
)
