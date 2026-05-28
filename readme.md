# 🛡️ Project GANDALF: Modular Security Sentinel

**GANDALF** is a proactive security suite developed in Python, designed to protect local file integrity, monitor hardware changes, and provide real-time web surveillance through global intelligence.

## 🚀 Core Features
- **DNA File Integrity:** Uses a dynamic sampling formula $(L^2 + 7)$ to extract unique byte signatures, combined with **SHA-256 hashing** to detect unauthorized modifications.
- **Self-Healing Vault:** Automatically restores critical `.py` files from a hidden secure backup if an intrusive change is detected.
- **Hardware Watchdog:** Real-time monitoring of USB ports via `psutil`, with instant Telegram alerts for unknown hardware detection.
- **Active Window Surveillance:** High-precision URL capture using `pygetwindow`, monitoring browser titles to intercept threats before they are executed.
- **Real-Time Downloads Guard:** Integrated `watchdog` monitoring in the system's `Downloads` directory to intercept, isolate, and move suspicious extensions to pre-quarantine before user execution.

## 🛠️ New Architectural Implementations
- **VirusTotal API v3 Integration:** Replaced legacy manual whitelists with a real-time connection to a global database of 70+ antivirus engines.
- **Interactive Telegram Command Center:** Implemented an asynchronous, bi-directional `callback_query_handler` using `InlineKeyboardMarkup`. It features byte-restricted callbacks (`short_name`) allowing remote users to trigger definitive quarantine or initiate local/cloud restorations.
- **Hybrid Cloud Restoration (`cloud_vault`):** Connected an index-managed restoration pipeline linked to Google Drive, capable of downloading and decrypting missing payloads automatically via unique Drive IDs.
- **Multi-Threaded Execution:** Implemented `threading` to run the "Visual Guard" and the "File Scanner" concurrently, ensuring the UI remains responsive ($T \approx 100ms$).
- **Fail-Safe Network Layer:** Custom `retry_request` engine in `network_utils.py` featuring a geometric backup delay ($5s, 10s, 20s\dots$) and a 5-minute critical hibernation protocol to endure severe internet drops without hanging active threads.
- **Os-Level Credential Vault:** Migrated all sensitive API keys, tokens, and master verification structures from flat files to the native OS secure storage using `keyring`.
- **Focused UI Context Utilities:** Centralized event handling via `gui_utils.py`, deploying a universal right-click clipboard menu utilizing coordinate-targeted `winfo_containing` to preserve widget focus.
- **Asynchronous UI Updates:** Uses the `.after()` method in `tkinter` to safely pass data from background threads to the main visual canvas.
- **Cloud-Canvas Aesthetics:** A custom-built UI using `PIL` (Pillow) with Gaussian Blur filters to create a modern, non-intrusive "Atmospheric" security dashboard.

## 🧠 Decision Logic & Math
The system balances security depth against system performance using **Calculus-based Optimization**.
- **Critical Point Analysis:** We define operational parameters where $B'(v) = 0$ to find the global maximum of protection vs. CPU overhead.
- **Entropy Control:** By analyzing file modifications through the second derivative of system logs, we distinguish between developer activity and malicious injection.

## 🛠️ Tech Stack
- **Languages:** Python 3.10+
- **Security Intelligence:** VirusTotal API v3.
- **Libraries:** `hashlib`, `psutil`, `requests`, `tkinter`, `PIL`, `pygetwindow`, `watchdog`, `keyring`, `telebot`.

## 🔍 Security Auditing & Compliance
Project GANDALF enforces strict static analysis and supply chain verification to guarantee architectural resilience.
- **Static Application Security Testing (SAST):** Evaluated locally using `bandit` across all $1700+$ lines of code to eliminate high-risk execution wrappers.
- **Dependency Vulnerability Scanning:** Verified via `safety scan` auditing all $100+$ environment packages against active CVE databases (**Status: 0 Vulnerabilities Reported**).
- **Continuous Automated Auditing:** Integrated with **GitHub CodeQL** to perform continuous data-flow analysis and cryptographic sanity checks on every remote state mutation.

## 🚀 Future Roadmap (The Monday Mission)
1. **Automated Quarantine Retention:** System-wide 30-day cleanup rotation of isolated threats to optimize local storage.
2. **Advanced Entropy Metrics:** Implementation of mathematical thresholds to evaluate real-time file structural deviation during runtime.