# 🛡️ Project GANDALF: Modular Security Sentinel

GANDALF is a proactive security suite developed in Python, designed to protect local file integrity, monitor hardware changes, and provide real-time web surveillance.

## 🚀 Core Features
- **DNA File Integrity:** Uses SHA-256 hashing to detect unauthorized modifications and triggers self-healing from a secure vault.
- **Hardware Watchdog:** Real-time monitoring of USB ports with Telegram alerts for unknown devices.
- **Active Web Shield:** Integrated with reputation APIs to analyze URLs and perform automated browser rollbacks (PyAutoGUI) upon threat detection.

## 🛠️ New Architectural Implementations
- **ACL (Access Control List):** A prioritized "Whitelist" layer to prevent false positives on trusted domains (Google, Microsoft, GitHub).
- **Network Intelligence:** Integration with URL Reputation APIs for global threat assessment.
- **Context Awareness:** Automated defensive actions (PyAutoGUI) only trigger when a web browser is the active window, preventing collateral system interference.

## 🧠 Decision Logic & Math
The system is built on **Bayesian Inference** models to balance sensitivity. We prioritize reducing *False Negatives* in critical file paths while minimizing *False Positives* during web browsing to ensure a smooth User Experience (UX).
I acknowledge that False Negatives are more critical than False Positives in the ecosystem; therefore, GANDALF is tuned to prioritize safety over convenience.

## 🛠️ Tech Stack
- **Languages:** Python 3.x
- **Libraries:** `hashlib`, `psutil`, `requests`, `tkinter`, `pyautogui`.

## 🚀 Future Roadmap (Next Steps)
1. **Centralized GUI:** A standalone dashboard to replace Telegram commands for professional monitoring.
2. **VPN Connectivity:** Implementation of an encrypted tunnel (VPN Connection) to secure all outgoing traffic.
3. **Global Scope:** Extending file surveillance to the entire OS, beyond the local project directory.
