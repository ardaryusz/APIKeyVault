import os
import json
import base64
import datetime
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Initialize the rich console
console = Console()

# --- SYSTEM-WIDE CONFIGURATION & PATHING ---
HOME_DIR = os.path.expanduser("~")
APP_DIR = os.path.join(HOME_DIR, "apivault")

if not os.path.exists(APP_DIR):
    os.makedirs(APP_DIR)

VAULT_FILE = os.path.join(APP_DIR, "vault.json")


# -------------------------------------------------

class APIKeyVault:
    def __init__(self):
        self.salt = None
        self.key = None
        self.cipher = None
        self.keys_data = []
        self.login_history = []

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def _record_login(self, status: str):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.login_history.append({"timestamp": timestamp, "status": status})

        if os.path.exists(VAULT_FILE):
            with open(VAULT_FILE, 'r') as f:
                data = json.load(f)

            data['login_history'] = self.login_history

            with open(VAULT_FILE, 'w') as f:
                json.dump(data, f)

    def initialize_vault(self, password: str):
        self.salt = os.urandom(16)
        self.key = self._derive_key(password, self.salt)
        self.cipher = Fernet(self.key)
        self.keys_data = []
        self.login_history = []

        self.save_vault()
        self._record_login("Success (Vault Created)")
        console.print(f"\n[bold green][+] Vault initialized securely at:[/bold green] [cyan]{VAULT_FILE}[/cyan]")

    def load_vault(self, password: str) -> bool:
        if not os.path.exists(VAULT_FILE):
            console.print("[bold red][-] Vault file not found. Please initialize first.[/bold red]")
            return False

        with open(VAULT_FILE, 'r') as f:
            data = json.load(f)

        self.salt = base64.b64decode(data['salt'])
        self.login_history = data.get('login_history', [])

        self.key = self._derive_key(password, self.salt)
        self.cipher = Fernet(self.key)

        try:
            decrypted_data = self.cipher.decrypt(data['encrypted_data'].encode())
            self.keys_data = json.loads(decrypted_data.decode())
            self._record_login("Success")
            return True
        except InvalidToken:
            self._record_login("Failed")
            console.print("\n[bold red][-] Incorrect master password or corrupted vault![/bold red]")
            return False

    def save_vault(self):
        if not self.cipher:
            return

        json_data = json.dumps(self.keys_data).encode()
        encrypted_data = self.cipher.encrypt(json_data).decode()

        vault_content = {
            'salt': base64.b64encode(self.salt).decode(),
            'encrypted_data': encrypted_data,
            'login_history': self.login_history
        }

        with open(VAULT_FILE, 'w') as f:
            json.dump(vault_content, f)

    def add_key(self, service: str, api_key: str, description: str):
        self.keys_data.append({
            "service": service,
            "key": api_key,
            "description": description
        })
        self.save_vault()
        console.print(f"\n[bold green][+] Key for '{service}' added successfully![/bold green]")

    def edit_key(self):
        query = console.input("\n[bold yellow]Enter search term for the key to edit:[/bold yellow] ").lower()
        results = [k for k in self.keys_data if query in k['service'].lower() or query in k['description'].lower()]

        if not results:
            console.print("\n[bold red][-] No matching keys found.[/bold red]")
            return

        self._render_keys_table(results, "Select Key to Edit")

        try:
            choice = int(console.input("\n[bold cyan]Select the number to edit (or 0 to cancel):[/bold cyan] "))
            if choice == 0:
                return
            if 1 <= choice <= len(results):
                selected = results[choice - 1]
                original_idx = self.keys_data.index(selected)

                console.print(
                    f"\n[bold]Editing '{selected['service']}'[/bold] [dim](Press Enter to keep current value)[/dim]")
                new_service = console.input(f"[cyan]Service[/cyan] [{selected['service']}]: ")
                new_key = console.input(f"[cyan]API Key[/cyan] [{selected['key']}]: ")
                new_desc = console.input(f"[cyan]Description[/cyan] [{selected['description']}]: ")

                if new_service.strip(): self.keys_data[original_idx]['service'] = new_service
                if new_key.strip(): self.keys_data[original_idx]['key'] = new_key
                if new_desc.strip(): self.keys_data[original_idx]['description'] = new_desc

                self.save_vault()
                console.print("\n[bold green][+] Key updated successfully![/bold green]")
            else:
                console.print("[bold red][-] Invalid selection.[/bold red]")
        except ValueError:
            console.print("[bold red][-] Please enter a valid number.[/bold red]")

    def remove_key(self):
        query = console.input("\n[bold yellow]Enter search term for the key to remove:[/bold yellow] ").lower()
        results = [k for k in self.keys_data if query in k['service'].lower() or query in k['description'].lower()]

        if not results:
            console.print("\n[bold red][-] No matching keys found.[/bold red]")
            return

        self._render_keys_table(results, "Select Key to Remove")

        try:
            choice = int(console.input("\n[bold cyan]Select the number to remove (or 0 to cancel):[/bold cyan] "))
            if choice == 0:
                return
            if 1 <= choice <= len(results):
                selected = results[choice - 1]
                confirm = console.input(
                    f"[bold red]Are you sure you want to permanently remove '{selected['service']}'? (y/n):[/bold red] ")

                if confirm.lower() == 'y':
                    self.keys_data.remove(selected)
                    self.save_vault()
                    console.print("\n[bold green][+] Key removed successfully![/bold green]")
                else:
                    console.print("[dim][-] Deletion cancelled.[/dim]")
            else:
                console.print("[bold red][-] Invalid selection.[/bold red]")
        except ValueError:
            console.print("[bold red][-] Please enter a valid number.[/bold red]")

    def _render_keys_table(self, results, title):
        """Helper function to render keys as stacked cards."""
        console.print(f"\n[bold magenta]--- {title} ---[/bold magenta]")

        for idx, k in enumerate(results, 1):
            # Stack the information vertically using newlines (\n)
            details = (
                f"[cyan]Service:[/cyan] {k['service']}\n"
                f"[white]Description:[/white] {k['description']}\n"
                f"[green]API Key:[/green] {k['key']}"
            )

            # Wrap each key in its own bordered panel
            card = Panel(details, title=f"[bold]Key #{idx}[/bold]", title_align="left", border_style="dim")
            console.print(card)

    def search_keys(self, query: str = ""):
        query = query.lower()
        results = [
            k for k in self.keys_data
            if query in k['service'].lower() or query in k['description'].lower()
        ]

        if not results:
            if query == "":
                console.print("\n[bold yellow][-] The vault is currently empty.[/bold yellow]")
            else:
                console.print("\n[bold red][-] No matching keys found.[/bold red]")
            return

        title = "All Keys in Vault" if query == "" else f"Search Results for '{query}'"
        console.print()  # Add a blank line for spacing
        self._render_keys_table(results, title)

    def change_password(self, new_password: str):
        self.salt = os.urandom(16)
        self.key = self._derive_key(new_password, self.salt)
        self.cipher = Fernet(self.key)
        self.save_vault()
        self._record_login("Success (Password Changed)")
        console.print("\n[bold green][+] Master password changed successfully![/bold green]")

    def view_login_history(self):
        if not self.login_history:
            console.print("\n[dim]No login history found.[/dim]")
            return

        table = Table(title="Recent Login Activity", show_header=True, header_style="bold magenta")
        table.add_column("Timestamp", style="dim")
        table.add_column("Status")

        recent_history = self.login_history[-15:]
        for entry in recent_history:
            status = entry['status']
            time = entry['timestamp']

            # Color code the status
            if "Failed" in status:
                status_text = Text(status, style="bold red")
            else:
                status_text = Text(status, style="bold green")

            table.add_row(time, status_text)

        console.print()
        console.print(table)


def main():
    vault = APIKeyVault()

    console.clear()
    console.print(Panel("[bold cyan]Secure API Key Vault[/bold cyan]", border_style="cyan", expand=False))

    if not os.path.exists(VAULT_FILE):
        console.print(f"[yellow]No vault found at[/yellow] [dim]{VAULT_FILE}[/dim]. [yellow]Let's set one up.[/yellow]")
        password = input("Create a Master Password: ")
        confirm = input("Confirm Master Password: ")
        if password != confirm:
            console.print("[bold red]Passwords do not match. Exiting.[/bold red]")
            return
        vault.initialize_vault(password)
        console.input("\n[dim]Press Enter to continue...[/dim]")
    else:
        password = input("Enter Master Password to unlock vault: ")
        if not vault.load_vault(password):
            return

    while True:
        console.clear()

        # Build the Dashboard Menu
        menu_text = (
            "[1] Add a new API Key\n"
            "[2] Edit an existing Key\n"
            "[3] Remove a Key\n"
            "[4] View all Keys\n"
            "[5] Search for a Key\n"
            "[6] Account\n"
            "[7] Lock and Exit"
        )
        console.print(
            Panel(menu_text, title="[bold green]Vault Dashboard[/bold green]", border_style="green", expand=False))

        choice = console.input("[bold cyan]Select an option (1-7):[/bold cyan] ")

        if choice == '1':
            service = console.input("\n[cyan]Service Name (e.g., OpenAI, Stripe):[/cyan] ")
            api_key = console.input("[cyan]API Key:[/cyan] ")
            desc = console.input("[cyan]Description/Notes:[/cyan] ")
            vault.add_key(service, api_key, desc)
            console.input("\n[dim]Press Enter to continue...[/dim]")

        elif choice == '2':
            vault.edit_key()
            console.input("\n[dim]Press Enter to continue...[/dim]")

        elif choice == '3':
            vault.remove_key()
            console.input("\n[dim]Press Enter to continue...[/dim]")

        elif choice == '4':
            vault.search_keys("")
            console.input("\n[dim]Press Enter to continue...[/dim]")

        elif choice == '5':
            query = console.input("\n[bold yellow]Enter search term:[/bold yellow] ")
            vault.search_keys(query)
            console.input("\n[dim]Press Enter to continue...[/dim]")

        elif choice == '6':
            while True:
                console.clear()
                acc_menu = (
                    "[1] Change Master Password\n"
                    "[2] View Login History\n"
                    "[3] Back to Main Menu"
                )
                console.print(Panel(acc_menu, title="[bold magenta]Account Menu[/bold magenta]", border_style="magenta",
                                    expand=False))

                acc_choice = console.input("[bold cyan]Select an option (1-3):[/bold cyan] ")

                if acc_choice == '1':
                    new_password = input("\nEnter new Master Password: ")
                    confirm = input("Confirm new Master Password: ")
                    if new_password != confirm:
                        console.print("\n[bold red][-] Passwords do not match. Password was NOT changed.[/bold red]")
                    else:
                        vault.change_password(new_password)
                    console.input("\n[dim]Press Enter to continue...[/dim]")
                elif acc_choice == '2':
                    vault.view_login_history()
                    console.input("\n[dim]Press Enter to continue...[/dim]")
                elif acc_choice == '3':
                    break
                else:
                    console.print("[bold red]Invalid option, please try again.[/bold red]")
                    console.input("\n[dim]Press Enter to continue...[/dim]")

        elif choice == '7':
            console.clear()
            console.print("[bold green]Vault locked. Goodbye![/bold green]\n")
            break
        else:
            console.print("[bold red]Invalid option, please try again.[/bold red]")
            console.input("\n[dim]Press Enter to continue...[/dim]")


if __name__ == "__main__":
    main()