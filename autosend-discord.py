import requests
import time
from datetime import datetime

# ====================== KONFIGURASI (EDIT DI SINI) ======================
# 1. Token akun Discord kamu (self-bot)
TOKEN = "wevawebubagevu"

# 2. Daftar Channel ID
CHANNEL_IDS = [
"1",
"2",
"3",
]

# 3. Daftar Pesan (urutan sesuai channel di atas)
PESAN_LIST = [
"""1""",
"""2""",
"""3""",
]

# 4. Pengaturan Waktu (dalam detik)
DELAY_ANTAR_CHANNEL = 2      # Jeda antar pengiriman (detik)
INTERVAL_LOOP = 7200          # 2 jam (720 detik), bisa diubah langsung

# 5. Webhook notifikasi (opsional, kosongkan "" jika tidak ingin)
WEBHOOK_URL = "https://discord.com/api/webhooks/"
# =======================================================================

def send_message(channel_id, message, token):
    """Mengirim satu pesan ke channel Discord."""
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    headers = {"Authorization": token, "Content-Type": "application/json"}
    payload = {"content": message}

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code == 200:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {channel_id}  terkirim")
            return True, ""
        elif resp.status_code == 429:  # Rate limited
            retry = resp.json().get('retry_after', 5)
            print(f"⚠️  Rate limited, tunggu {retry:.1f} detik...")
            time.sleep(retry)
            return send_message(channel_id, message, token)
        else:
            msg = f"❌ Gagal {channel_id} — status {resp.status_code}: {resp.text}"
            print(msg)
            return False, msg
    except Exception as e:
        msg = f"❌ Error: {e}"
        print(msg)
        return False, msg

def send_webhook(content):
    """Mengirim notifikasi ke webhook Discord (jika URL diisi)."""
    if not WEBHOOK_URL:
        return
    try:
        requests.post(WEBHOOK_URL, json={"content": content}, timeout=10)
    except Exception as e:
        print(f"⚠️  Gagal kirim webhook: {e}")

def main():
    # Validasi jumlah channel dan pesan harus sama
    if len(CHANNEL_IDS) != len(PESAN_LIST):
        print("❌ ERROR: Jumlah channel dan pesan tidak sama!")
        print(f"   Channel: {len(CHANNEL_IDS)}, Pesan: {len(PESAN_LIST)}")
        return

    total = len(CHANNEL_IDS)
    print(f"===== DISCORD AUTO MESSENGER ({total} CHANNEL, PESAN BERBEDA) =====")
    print(f"Loop interval: {INTERVAL_LOOP//3600} jam")
    print(f"Jumlah channel: {total}")
    if WEBHOOK_URL:
        print("Notifikasi webhook: AKTIF")
    else:
        print("Notifikasi webhook: TIDAK AKTIF")
    print("Tekan Ctrl+C untuk berhenti.\n")

    while True:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n--- Batch {timestamp} ---")
        sukses = 0
        errors = []

        for i in range(total):
            ch_id = str(CHANNEL_IDS[i])
            pesan = PESAN_LIST[i]
            print(f"[{i+1}/{total}] Mengirim ke {ch_id}...")
            status, err = send_message(ch_id, pesan, TOKEN)
            if status:
                sukses += 1
            else:
                errors.append(f"• <#{ch_id}>: {err}")
            if i < total - 1:
                time.sleep(DELAY_ANTAR_CHANNEL)

        # Ringkasan terminal
        print(f"Batch selesai: {sukses}/{total} terkirim.")
        if errors:
            print("Error:")
            for e in errors:
                print(e)

        # Notifikasi webhook (ringkasan batch)
        notif = f"📊 **Batch {timestamp}**\n✅ {sukses}/{total} pesan terkirim."
        if errors:
            notif += "\n❌ Gagal:\n" + "\n".join(errors[:5])
        notif += f"\n⏳ Menunggu {INTERVAL_LOOP//3600} jam..."
        send_webhook(notif)

        print(f"⏳ Menunggu {INTERVAL_LOOP//3600} jam...")
        time.sleep(INTERVAL_LOOP)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Program dihentikan.")
