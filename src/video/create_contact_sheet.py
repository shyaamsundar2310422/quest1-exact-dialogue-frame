import os
import cv2
import math


INPUT_DIR = "data/samples/full_scan"
OUTPUT_PATH = "data/samples/full_video_contact_sheet.jpg"

THUMB_WIDTH = 240
THUMB_HEIGHT = 180
COLUMNS = 5


def create_contact_sheet():
    files = sorted(
        [
            f for f in os.listdir(INPUT_DIR)
            if f.lower().endswith(".jpg")
        ]
    )

    if not files:
        raise RuntimeError("No sample frames found.")

    rows = math.ceil(len(files) / COLUMNS)

    sheet = cv2.UMat(
        rows * THUMB_HEIGHT,
        COLUMNS * THUMB_WIDTH,
        cv2.CV_8UC3
    )

    sheet_mat = sheet.get()

    for index, filename in enumerate(files):
        path = os.path.join(INPUT_DIR, filename)

        image = cv2.imread(path)

        if image is None:
            continue

        image = cv2.resize(
            image,
            (THUMB_WIDTH, THUMB_HEIGHT)
        )

        # Extract timestamp from filename:
        # scan_0000.0.jpg
        timestamp = filename.replace("scan_", "").replace(".jpg", "")

        cv2.putText(
            image,
            f"{timestamp}s",
            (8, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

        cv2.putText(
            image,
            f"{timestamp}s",
            (8, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 0),
            1
        )

        row = index // COLUMNS
        col = index % COLUMNS

        y1 = row * THUMB_HEIGHT
        y2 = y1 + THUMB_HEIGHT

        x1 = col * THUMB_WIDTH
        x2 = x1 + THUMB_WIDTH

        sheet_mat[y1:y2, x1:x2] = image

    cv2.imwrite(OUTPUT_PATH, sheet_mat)

    print(f"Created contact sheet: {OUTPUT_PATH}")
    print(f"Frames included: {len(files)}")


if __name__ == "__main__":
    create_contact_sheet()