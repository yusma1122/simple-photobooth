import cv2
from PIL import Image
import time
import os
from datetime import datetime

# Direktori output
OUTPUT_DIR = r"G:\My Drive\Photobooth"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Frame overlay
FRAME_PATH = 'bingkai.png'  # Harus PNG transparan

def overlay_frame(photo_path, frame_path, output_path):
    foto = Image.open(photo_path).convert("RGBA")
    bingkai = Image.open(frame_path).convert("RGBA")

    if foto.size != bingkai.size:
        bingkai = bingkai.resize(foto.size)

    hasil = Image.alpha_composite(foto, bingkai)
    hasil.save(output_path)
    print(f"✅ Hasil akhir disimpan sebagai '{output_path}'")

def photo_booth():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Kamera tidak tersedia.")
        return

    print("📷 Tekan 's' untuk mulai foto dengan countdown. Tekan 'q' untuk keluar.")

    countdown = 5
    temp_path = os.path.join(OUTPUT_DIR, "temp_capture.png")
    countdown_started = False
    start_time = None

    # Load bingkai PNG sebagai transparan overlay
    frame_overlay = cv2.imread(FRAME_PATH, cv2.IMREAD_UNCHANGED)  # Baca dengan alpha

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize overlay agar pas dengan frame kamera
        if frame_overlay is not None:
            overlay_resized = cv2.resize(frame_overlay, (frame.shape[1], frame.shape[0]))

            # Pisahkan channel alpha jika ada
            if overlay_resized.shape[2] == 4:
                overlay_rgb = overlay_resized[:, :, :3]
                overlay_alpha = overlay_resized[:, :, 3] / 255.0 * 0.5  # Transparansi 50%

                for c in range(3):
                    frame[:, :, c] = (overlay_alpha * overlay_rgb[:, :, c] +
                                      (1 - overlay_alpha) * frame[:, :, c]).astype('uint8')

        # Countdown
        if countdown_started:
            elapsed = time.time() - start_time
            remaining = countdown - int(elapsed)

            if remaining > 0:
                countdown_text = str(remaining)
                font = cv2.FONT_HERSHEY_DUPLEX
                font_scale = 6
                text_color = (255, 255, 255)
                outline_color = (0, 0, 0)
                thickness = 10
                alpha = 0.6  # Transparansi overlay

                # Salin frame untuk overlay
                overlay = frame.copy()

                # Buat background gelap semi-transparan
                bg_overlay = frame.copy()
                bg_color = (0, 0, 0)
                cv2.rectangle(bg_overlay, (0, 0), (frame.shape[1], frame.shape[0]), bg_color, -1)
                cv2.addWeighted(bg_overlay, 0.4, overlay, 0.6, 0, overlay)

                # Hitung ukuran dan posisi teks
                text_size, _ = cv2.getTextSize(countdown_text, font, font_scale, thickness)
                text_x = int((frame.shape[1] - text_size[0]) / 2)
                text_y = int((frame.shape[0] + text_size[1]) / 2)

                # Teks dengan outline hitam
                cv2.putText(overlay, countdown_text, (text_x, text_y), font, font_scale, outline_color, thickness + 4, cv2.LINE_AA)
                cv2.putText(overlay, countdown_text, (text_x, text_y), font, font_scale, text_color, thickness, cv2.LINE_AA)

                # Gabungkan overlay ke frame
                cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

            else:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = os.path.join(OUTPUT_DIR, f"hasil_{timestamp}.png")

                cv2.imwrite(temp_path, frame)
                time.sleep(0.2)

                if os.path.exists(temp_path):
                    overlay_frame(temp_path, FRAME_PATH, output_path)
                    os.remove(temp_path)
                    print(f"📸 Foto disimpan sebagai '{output_path}' dengan frame.")
                else:
                    print("❌ Gagal menyimpan foto sementara.")

                countdown_started = False  # Reset

        cv2.imshow("Photo Booth - Tekan 's' untuk Foto", frame)
        key = cv2.waitKey(1)

        if key == ord('s') and not countdown_started:
            countdown_started = True
            start_time = time.time()
            print("⏳ Countdown dimulai...")

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("📁 Selesai.")


if __name__ == "__main__":
    photo_booth()
