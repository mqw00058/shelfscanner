import cv2
import numpy as np
from pathlib import Path

from backend.config import (
    BLUR_THRESHOLD,
    MAX_FRAMES,
    MIN_SHARPNESS_SCORE,
    MOTION_BLUR_THRESHOLD,
)

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}


def is_video(file_path: str) -> bool:
    return Path(file_path).suffix.lower() in VIDEO_EXTENSIONS


def is_image(file_path: str) -> bool:
    return Path(file_path).suffix.lower() in IMAGE_EXTENSIONS


# ----------------------------------------------------------------
# Blur / sharpness detection
# ----------------------------------------------------------------

def compute_sharpness(frame: np.ndarray) -> float:
    """Laplacian variance — higher = sharper."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def detect_motion_blur(frame: np.ndarray) -> float:
    """Detect directional motion blur using Sobel gradient ratio.

    Returns a score: higher = less motion blur.
    If horizontal and vertical gradients are very unbalanced the frame
    likely has directional motion blur.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    gx = np.mean(np.abs(sobel_x))
    gy = np.mean(np.abs(sobel_y))
    if max(gx, gy) == 0:
        return 0.0
    # Ratio close to 1.0 = balanced (no directional blur)
    ratio = min(gx, gy) / max(gx, gy)
    # Combine with overall gradient magnitude
    magnitude = (gx + gy) / 2.0
    return ratio * magnitude


def is_frame_sharp(frame: np.ndarray) -> tuple[bool, float]:
    """Check if a frame is sharp enough for analysis.

    Returns (is_sharp, sharpness_score).
    """
    sharpness = compute_sharpness(frame)
    motion_score = detect_motion_blur(frame)

    if sharpness < BLUR_THRESHOLD:
        return False, sharpness
    if motion_score < MOTION_BLUR_THRESHOLD:
        return False, sharpness
    return True, sharpness


def enhance_frame(frame: np.ndarray) -> np.ndarray:
    """Sharpen and enhance contrast for better OCR / text readability."""
    # Denoise
    denoised = cv2.fastNlMeansDenoisingColored(frame, None, 6, 6, 7, 21)

    # CLAHE on L channel for contrast enhancement
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # Unsharp mask for sharpening
    gaussian = cv2.GaussianBlur(enhanced, (0, 0), 3)
    sharpened = cv2.addWeighted(enhanced, 1.5, gaussian, -0.5, 0)

    return sharpened


# ----------------------------------------------------------------
# Frame extraction
# ----------------------------------------------------------------

def extract_key_frames(file_path: str, max_frames: int = MAX_FRAMES) -> list[np.ndarray]:
    """Extract sharp, high-quality key frames from video or load image."""
    if is_image(file_path):
        frame = cv2.imread(file_path)
        if frame is None:
            raise ValueError(f"Cannot read image: {file_path}")
        sharp, score = is_frame_sharp(frame)
        # For single images, enhance even if slightly blurry
        if score < BLUR_THRESHOLD * 2:
            frame = enhance_frame(frame)
        return [frame]

    if not is_video(file_path):
        raise ValueError(f"Unsupported file type: {Path(file_path).suffix}")

    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {file_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30

    if total_frames <= 0:
        cap.release()
        raise ValueError("Video has no frames")

    # Collect many candidate frames, then pick the sharpest ones
    candidates = _collect_candidates(cap, total_frames, fps, max_frames)
    cap.release()

    if not candidates:
        raise ValueError("No sharp frames found in video. Try recording more slowly.")

    # Sort by sharpness (best first) and pick top N
    candidates.sort(key=lambda x: x[1], reverse=True)

    selected = []
    used_positions = []
    min_gap = max(1, total_frames // (max_frames * 3))

    for frame_idx, score, frame in candidates:
        if len(selected) >= max_frames:
            break
        # Avoid picking frames too close together (same shelf section)
        if all(abs(frame_idx - pos) > min_gap for pos in used_positions):
            # Enhance frame for better text readability
            enhanced = enhance_frame(frame)
            selected.append(enhanced)
            used_positions.append(frame_idx)

    print(f"Frame extraction: {len(selected)} sharp frames from {total_frames} total "
          f"({len(candidates)} candidates evaluated)")

    return selected


def _collect_candidates(
    cap, total_frames: int, fps: float, max_frames: int
) -> list[tuple[int, float, np.ndarray]]:
    """Sample frames across the video and filter by sharpness.

    Returns list of (frame_index, sharpness_score, frame).
    """
    # Sample more densely than before: every 0.3 seconds or so
    sample_step = max(1, int(fps * 0.3))
    # But cap total samples to avoid slowness on very long videos
    max_samples = max_frames * 20
    if total_frames // sample_step > max_samples:
        sample_step = total_frames // max_samples

    candidates = []
    prev_hist = None

    for i in range(0, total_frames, sample_step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret or frame is None:
            continue

        # Quick scene-similarity check: skip if too similar to last kept candidate
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [64], [0, 256])
        cv2.normalize(hist, hist)

        if prev_hist is not None:
            corr = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
            if corr > 0.98:
                # Too similar to previous — skip
                continue

        # Sharpness check
        sharp, score = is_frame_sharp(frame)
        if sharp and score >= MIN_SHARPNESS_SCORE:
            candidates.append((i, score, frame))
            prev_hist = hist

    # If no sharp frames found, relax threshold and try again
    if not candidates:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        relaxed_threshold = BLUR_THRESHOLD * 0.5
        sample_step_relaxed = max(1, int(fps * 1.0))

        for i in range(0, total_frames, sample_step_relaxed):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret or frame is None:
                continue
            score = compute_sharpness(frame)
            if score >= relaxed_threshold:
                candidates.append((i, score, frame))

    return candidates
