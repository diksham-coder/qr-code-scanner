import cv2
from pyzbar import pyzbar
from datetime import datetime
import csv
import os

# Store unique barcodes
scanned_codes = set()

# CSV file setup
FILE_NAME = "scan_history.csv"
if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Type", "Data", "Timestamp"])


def read_barcodes(frame):
    """
    Detect and decode barcodes/QR codes from the frame
    """
    global scanned_codes

    # Convert to grayscale for better detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    barcodes = pyzbar.decode(gray)

    for barcode in barcodes:
        barcode_data = barcode.data.decode('utf-8')
        barcode_type = barcode.type

        # Check for duplicate scan
        if barcode_data not in scanned_codes:
            scanned_codes.add(barcode_data)
            timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            # Save to CSV
            with open(FILE_NAME, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([barcode_type, barcode_data, timestamp])

            print(f"Detected {barcode_type}: {barcode_data} at {timestamp}")

        # Draw bounding box
        x, y, w, h = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        text = f"{barcode_type}"
        cv2.putText(frame, text, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    return frame


def main():
    """
    Main function to run the barcode scanner
    """
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Error: Could not open camera")
        return

    print("Barcode / QR Code Scanner Started")
    print("Press 'q' to quit")

    while True:
        ret, frame = camera.read()
        if not ret:
            break

        frame = read_barcodes(frame)

        # Display total scan count
        cv2.putText(frame, f"Total Unique Scans: {len(scanned_codes)}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255, 255, 255), 2)

        cv2.putText(frame, "Press 'q' to quit",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (255, 255, 255), 2)

        cv2.imshow("Barcode / QR Code Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()
    print("Scanner closed")


if __name__ == "__main__":
    main()

