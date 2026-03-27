# 🛡️ Project GANDALF: Modular Security Sentinel

GANDALF is a proactive security suite developed in Python, designed to protect local file integrity, monitor hardware changes, and provide real-time web surveillance.

## 🚀 Core Features
- **DNA File Integrity:** Uses SHA-256 hashing to detect unauthorized modifications and triggers self-healing from a secure vault.
- **Hardware Watchdog:** Real-time monitoring of USB ports with Telegram alerts for unknown devices.
- **API-Driven Firewall:** A localized **Flask server** that intercepts browser traffic in real-time for immediate threat analysis, replacing legacy UI-automation methods.

## 🛠️ New Architectural Implementations
- **Multi-Threaded Execution:** Uses the `threading` library to run the file integrity scanner and the network firewall concurrently, ensuring zero performance bottlenecks.
- **Client-Server Model:** Shifted to a robust internal API. GANDALF now acts as a listener (Port 5000) for external browser hooks, ensuring 100% URL capture reliability.
- **ACL (Access Control List):** A prioritized "Whitelist" layer to prevent false positives on trusted domains (Google, Microsoft, GitHub).
- **Context Awareness:** Defensive actions (PyAutoGUI) are intelligently triggered only when a web browser is the active window, preventing collateral system interference.

## 🧠 Decision Logic & Math
The system's sensitivity and performance are tuned using **Calculus-based Optimization**. I use differential calculus to find the "Critical Points" ($B'(v) = 0$) where system protection is maximized relative to CPU resource consumption.
By analyzing the **Second Derivative**, I ensure our operational parameters sit at a global maximum, balancing security depth with a seamless User Experience (UX). I prioritize reducing *False Negatives* in critical file paths while maintaining safety over convenience.

## 🛠️ Tech Stack
- **Languages:** Python 3.x
- **Network Stack:** `Flask`, `Flask-CORS`, `threading`.
- **Libraries:** `hashlib`, `psutil`, `requests`, `tkinter`, `pyautogui`.

## 🚀 Future Roadmap (Next Steps)
1. **Chrome Extension Integration:** Finalizing the native JavaScript hook for seamless URL dispatching.
2. **Centralized GUI:** A standalone dashboard to replace Telegram commands for professional monitoring.
3. **Encrypted Tunneling:** Implementation of a VPN/Proxy layer for global traffic encryption and privacy.
