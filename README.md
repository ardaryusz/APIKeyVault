# Secure API Key Vault

A fully local, encrypted, and beautifully styled command-line interface (CLI) for managing your developer API keys and sensitive tokens. 

Built with Python, secured by AES (Fernet) encryption, and styled with `rich`.

---

## Features

* **Military-Grade Encryption:** Your keys are encrypted locally using AES (via the `cryptography` library). They are never stored in plain text.
* **Brute-Force Protection:** Master passwords are run through PBKDF2HMAC with 480,000 iterations to derive the encryption key, neutralizing brute-force attacks.
* **Smart Search:** Instantly filter your vault by service name or description.
* **Login Tracking:** Keeps an audited history of the last 15 successful and failed login attempts to monitor for unauthorized access.
* **Global Command:** Installs directly to your system path, allowing you to open your vault by typing `keyvault` from any directory.
* **Portable & Hidden:** Automatically creates a hidden `apivault` folder in your home directory to safely store your encrypted data away from your working code.

## Installation

### Prerequisites
* Python 3.7 or higher installed on your system.

### Option 1: Automatic Install (Windows)
1. Clone this repository:
   ```bash
   git clone https://github.com/ardaryusz/APIKeyVault.git
   cd APIKeyVault
   start setup.bat
   ```
2. Select **Option 1** to automatically install the requirements and register the command.

### Option 2: Manual Install (Mac/Linux/Windows)
1. Clone this repository and navigate into the folder:
   ```bash
   git clone https://github.com/ardaryusz/APIKeyVault.git
   ```
2. Run the pip install command:
   ```bash
   pip install -e .
   ```

## Usage

Once installed, simply open a new terminal window anywhere on your computer and type:

```bash
keyvault
```

### First Run
The first time you run the application, it will prompt you to create a **Master Password**. Make sure you remember this! If you lose it, your vault **cannot** be recovered.

### Dashboard Options
* **[1] Add a new API Key:** Store a new service, key, and notes.
* **[2] Edit an existing Key:** Modify details of an already saved key (leave fields blank to keep current values).
* **[3] Remove a Key:** Permanently delete a key from the vault.
* **[4] View all Keys:** Display all keys.
* **[5] Search for a Key:** Find a specific key by typing part of the service name or description.
* **[6] Account:** Change your Master Password or view recent login activity.
* **[7] Lock and Exit:** Safely lock the vault and clear the terminal.

## Security Architecture

1. **The Salt:** When you initialize a vault, a random 16-byte cryptographic salt is generated.
2. **Key Derivation:** Your Master Password and the salt are processed through `PBKDF2HMAC` (SHA-256) 480,000 times to create a highly secure 32-byte encryption key.
3. **Encryption:** Your API keys are serialized into JSON and encrypted using `Fernet` (which guarantees that a message encrypted using it cannot be manipulated or read without the key).
4. **In-Memory Operations:** Keys are only decrypted in your computer's RAM while the script is actively running. 

## Uninstallation

If you ever want to remove the tool from your system:

* **Standard Uninstall:** Double-click `setup.bat` and select **Option 2**.
* **Full Uninstall:** Double-click `setup.bat` and select **Option 3**.
* **Manual:** Run `pip uninstall keyvault -y` in your terminal.

*(Note: Uninstalling the program does not delete your encrypted `vault.json` file unless you select option 3.*)
