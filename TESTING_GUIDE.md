# QA and Testing Environment Guide - Project GANDALF

This document outlines the standard operational procedure for deploying an isolated test laboratory using a Virtual Machine (Sandbox). This setup allows the verification of feature injections, hardware (USB) detection, and the automated hotfix update engine without altering the host operating system.

## 1. Laboratory Requirements
- **Hypervisor:** Oracle VM VirtualBox (v7.0+ or higher).
- **Extension Pack:** VirtualBox Extension Pack (Mandatory for bridging hardware USB 2.0/3.0 controller buses).
- **Base Image:** Official Windows 10/11 ISO (A clean environment free of prior Python or PyCharm dependencies).

## 2. Virtual Machine Configuration
1. Create a new virtual instance, allocating a minimum of **4 GB RAM** and **2 vCPUs**.
2. Mount the downloaded ISO image and proceed with a clean operating system installation.
3. Once inside the OS, install the VirtualBox *Guest Additions* to enable screen synchronization and the bidirectional **Drag and Drop** feature.

## 3. Hardware Testing Protocol (USB Passthrough)
To audit Gandalf's capability to intercept `WM_DEVICECHANGE` window messages or WMI passive ejection driver calls:

1. Connect the physical USB testing device into the host (real) computer.
2. In the Virtual Machine window menu, navigate to: `Devices` -> `USB`.
3. Select the corresponding hardware identifier. The host system will release control of the device, and the virtual bus will mount it internally ($T \approx 0ms$).
4. Validate the behavioral response of Gandalf's active background surveillance threads.

## 4. Remote Update Cycle Simulation (Hotfix/Releases)
To verify that the `updater.py` engine and the execution bridge scripts (`.bat` / `.sh`) cleanly handle the running binary mutation:

1. Compile Gandalf into a single standalone file from your development environment:
   ```bash
   pyinstaller --clean Gandalf_key.spec
   
# 5. Activate File Transfer: Shared Folders (Fail-safe Method)
If the host operating system restricts bidirectional Drag & Drop features due to UAC (User Account Control) integrity level mismatches, a permanent shared folder architecture must be deployed:

1. In the Virtual Machine menu bar, navigate to `Devices` -> `Shared Folders` -> `Shared Folders Settings...`.
2. Click the `Add Share` button (+) and configure the following parameters:
   - **Folder Path:** Point to the local machine development output directory (e.g., `...\gandalfkey\dist`).
   - **Folder Name:** Keep the default generic identifier (e.g., `dist`).
   - **Mount Options:** Check **Auto-mount** and **Make Permanent**.
3. Inside the virtual Windows 11 guest instance, open `This PC`. The shared directory will be mounted as a network location drive (`\\VBOXSVC\dist`).

This guarantees instantaneous access to compiled binary builds without network overhead or permission drops.