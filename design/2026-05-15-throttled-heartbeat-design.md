# Design Document - Throttled Heartbeat & Result-Based Translation

## Objective
Reduce unnecessary OCR and translation calls during continuous screen movement (scrolling, animations) to improve UX and reduce CPU usage.

## Problem Statement
The current system is over-reactive to pixel changes. When the screen moves continuously, it triggers an "OCR storm," performing expensive operations on transient frames. This leads to high CPU usage and "flickering" translations that are immediately replaced.

## Proposed Design: The "Intelligent Sentry"

### 1. State-Based Throttling
The `TranslationWorker` will manage a "Moving" vs. "Stationary" state.

- **Stationary Mode:** High-sensitivity mode. Wakes up immediately on pixel change.
- **Moving Mode:** Triggered when consecutive frame changes are detected within a short window.
- **Heartbeat:** While in "Moving Mode," the system throttles OCR/Translation to a maximum of one cycle every **1.5 seconds**.

### 2. Result-First Translation Logic
Decouple visual change from semantic change.
- Pixel changes are treated as "hints" to check for text.
- Before calling the Translation API, the stable OCR result is compared against the last translated text.
- If the text is semantically identical (or very high similarity), the translation call is skipped.

### 3. Components & Data Flow
- **`TranslationWorker`:** 
    - Tracks `last_translate_time` and `is_moving`.
    - Implements adaptive `time.sleep` based on state.
    - Manages the `ocr_buffer` with an explicit clear when a significant new movement starts.
- **`OCRService`:** 
    - Continues to provide robust text extraction.
- **`TranslationService`:** 
    - Only invoked when `new_text != last_text`.

## Success Criteria
- CPU usage drops significantly during continuous scrolling.
- Translation overlay doesn't flicker during movement.
- System responds instantly ( < 300ms) when the screen becomes still again.
