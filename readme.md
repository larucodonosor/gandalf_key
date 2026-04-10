# 🛡️ Project GANDALF: Modular Security Sentinel

**GANDALF** is a proactive security suite developed in Python, designed to protect local file integrity, monitor hardware changes, and provide real-time web surveillance through global intelligence.

## 🚀 Core Features
- **DNA File Integrity:** Uses a dynamic sampling formula $(L^2 + 7)$ to extract unique byte signatures, combined with **SHA-256 hashing** to detect unauthorized modifications.
- **Self-Healing Vault:** Automatically restores critical `.py` files from a hidden secure backup if an intrusive change is detected.
- **Hardware Watchdog:** Real-time monitoring of USB ports via `psutil`, with instant Telegram alerts for unknown hardware detection.
- **Active Window Surveillance:** High-precision URL capture using `pygetwindow`, monitoring browser titles to intercept threats before they are executed.

## 🛠️ New Architectural Implementations
- **VirusTotal API v3 Integration:** Replaced legacy manual whitelists with a real-time connection to a global database of 70+ antivirus engines.
- **Multi-Threaded Execution:** Implemented `threading` to run the "Visual Guard" and the "File Scanner" concurrently, ensuring the UI remains responsive ($T \approx 100ms$).
- **Asynchronous UI Updates:** Uses the `.after()` method in `tkinter` to safely pass data from background threads to the main visual canvas.
- **Cloud-Canvas Aesthetics:** A custom-built UI using `PIL` (Pillow) with Gaussian Blur filters to create a modern, non-intrusive "Atmospheric" security dashboard.

## 🧠 Decision Logic & Math
The system balances security depth against system performance using **Calculus-based Optimization**.
- **Critical Point Analysis:** We define operational parameters where $B'(v) = 0$ to find the global maximum of protection vs. CPU overhead.
- **Entropy Control:** By analyzing file modifications through the second derivative of system logs, we distinguish between developer activity and malicious injection.

## 🛠️ Tech Stack
- **Languages:** Python 3.10+
- **Security Intelligence:** VirusTotal API v3.
- **Libraries:** `hashlib`, `psutil`, `requests`, `tkinter`, `PIL`, `pygetwindow`, `python-dotenv`.

## 🚀 Future Roadmap (The Monday Mission)
1. **Recursive PC Scanning:** Expanding beyond local folders to monitor "Hot Zones" (Downloads, Desktop).
2. **Quarantine Management:** Automatic 30-day cleanup of isolated threats to optimize disk space.
3. **Telegram Command Center:** Implementation of `/status` and `/unlock` protocols for remote management.