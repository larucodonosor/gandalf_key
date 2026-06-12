_English:_
# Gandalf_key: Deployment & Installation Guide 🪄

Welcome to the installation matrix. Gandalf can be deployed via two methods depending on your profile: **Easy Mode** (For general users/No-Tech) or **Technical Mode** (For developers).

## Method 1: Easy Mode (Recommended for quick setup ⚡

This method does not require Python, Git, or terminal execution. Everything is packaged into a standalone secure bundle.

### Prerequisites
- **Operating System:** Windows 10 / 11
- **Privileges:** Administrative rights (Required to monitor hardware and USB ports).

### Step-by-Step Setup
1. **Download the Bundle:** Download the `Gandalf_key_v1.0.zip` file from the **Latest Release** section on GitHub.
2. **Extract:** Unzip the folder anywhere on your local storage (e.g., Desktop).
3. **Launch:** Right-click `main.exe` and select **Run as Administrator**.
4. **Configuration Wizard:** The first time Gandalf boots, an automated Setup Wizard will appear:
   - Insert your Master Key configuration parameters.
   - Securely type your Telegram Token, Chat ID, VirusTotal API Key and Google OAuth credentials (Client ID and Secret ID) directly into the visual interface fields.
   - *Gandalf will automatically provision these tokens into your Windows Secure Credential Manager (Keyring) behind the scenes.*

---

## Method 2: Technical Mode (Source Code Deployment) 💻
Use this environment setup if you wish to audit, modify, or run the sentinel from the Python raw interpreter.

## Prerequisites
Ensure your system meets the following environment baselines:
- **Operating System:** Windows 10 / 11 (Required for native `keyring` and Windows API surveillance tools).
- **Python Version:** Python 3.10 to Python 3.12 (Recommended).
- **Permissions:** Administrative Privileges (Required for `psutil` hardware monitoring).

## Installation Steps

### 1. Clone the Repository
Open your terminal and pull the project files to your local environment:
```bash
git clone [https://github.com/YOUR_USERNAME/gandalfkey.git](https://github.com/YOUR_USERNAME/gandalfkey.git)
cd gandalfkey
```

### 2. Set Up a Virtual Environment (Recommended)
To isolate project dependencies to prevent conflicts with local Python libraries:

```bash
python -m venv venv
# Activate:
.\venv\Scripts\activate
```

### 3. Install Core Dependencies
Deploy the required security, graphics, and system libraries listed in the setup:

```bash
pip install -r requirements.txt
```

### 4. Execute Gandalf_key
Launch the main application controller whit elevated privileges:

```bash
python src/main.py
```

### 5. In_App Keyring Provisioning
Once the UI initializes, the application will detect that the environment lacks credentials and will prompt the setup configuration panels. 
Fill in your credentials inside the fields. 
The backend script will link with keyring and store your parameters natively without exposing raw files.

## Critical Post-Deployment Configurations
### 1. How to Bypass Windows Defender (False Positives)
Because Gandalf interacts with your storage, encrypts files, and runs background monitoring tasks, Windows Defender might flag the standalone .exe as an unrecognized program.
- **To bypass this protection:**
- When running Gandalf_key.exe for the first time, click on the "More info" (Más información) link inside the Windows SmartScreen blue pop-up.
- Click the "Run anyway" (Ejecutar de todas formas) button that appears at the bottom.
- Pro-Tip (Avoid continuous scanning): To prevent Windows Defender from continuously checking Gandalf's working directories, open Windows Security -> Virus & threat protection -> Manage settings -> Exclusions (Exclusiones). Add the extracted Gandalf_key folder there to whitelist the wizard.

### 2. Setting Up Automatic Boot (Persistence)
If you completely shut down your computer, you can anchor Gandalf to the Windows boot sequence so he starts his watch automatically.
- **Option A:** The Startup Folder (Easiest)
- Press Win + R on your keyboard to open the Run dialog.
- Type shell:startup and hit Enter to open your Windows Startup folder.
- Right-click your Gandalf_key.exe file and select Create shortcut (Crear acceso directo).
- Cut and paste that new shortcut directly into the Startup folder.
- **Option B:** Windows Task Scheduler (Stealth & Silent Boot)
To make Gandalf launch silently without flashing any temporary console windows:
- Open the Windows Start Menu, search for Task Scheduler (Programador de Tareas) and open it.
- Click Create Basic Task... (Crear Tarea Básica) on the right panel. Name it Gandalf Guard.
- Set the Trigger to When I log on (Al iniciar sesión).
- Set the Action to Start a program and browse to select your Gandalf_key.exe.
- Finish the wizard, open the task properties, and ensure it runs with highest privileges.

“Keep it secret. Keep it safe.” 🗝️🔒
