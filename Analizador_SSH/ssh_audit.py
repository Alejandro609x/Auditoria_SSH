#!/usr/bin/env python3

import paramiko
import getpass
import socket
import re
import os
import time
from rich.console import Console
from rich.panel import Panel
from rich import print

console = Console()


class SSHAudit:

    def __init__(self, host, username, password, port=22):

        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.client = None

        self.report = []

    # =========================================
    # LOG
    # =========================================

    def log(self, text):

        self.report.append(text)

    # =========================================
    # CONNECT
    # =========================================

    def connect(self):

        try:

            self.client = paramiko.SSHClient()

            self.client.set_missing_host_key_policy(
                paramiko.AutoAddPolicy()
            )

            self.client.connect(
                hostname=self.host,
                username=self.username,
                password=self.password,
                port=self.port,
                timeout=10,
                allow_agent=False,
                look_for_keys=False
            )

            console.print(
                f"[green][+] Conectado a {self.host}[/green]"
            )

            self.log(
                f"[+] Conectado a {self.host}"
            )

            return True

        except socket.timeout:

            console.print(
                "[red][-] Timeout[/red]"
            )

        except paramiko.AuthenticationException:

            console.print(
                "[red][-] Credenciales inválidas[/red]"
            )

        except Exception as e:

            console.print(
                f"[red][-] Error: {e}[/red]"
            )

        return False

    # =========================================
    # EXECUTE COMMAND
    # =========================================

    def run(self, cmd):

        stdin, stdout, stderr = self.client.exec_command(
            cmd
        )

        output = stdout.read().decode(
            errors="ignore"
        )

        error = stderr.read().decode(
            errors="ignore"
        )

        return output + error

    # =========================================
    # SECTION
    # =========================================

    def section(self, title):

        console.print(
            Panel.fit(
                title,
                style="bold cyan"
            )
        )

        self.log("\n" + "=" * 70)

        self.log(title)

        self.log("=" * 70)

    # =========================================
    # GENERIC CHECK
    # =========================================

    def execute_check(self, title, cmd):

        self.section(title)

        result = self.run(cmd)

        print(result)

        self.log(result)

    # =========================================
    # SEARCH TMP EXECUTIONS
    # =========================================

    def tmp_executions(self):

        self.section(
            "Scripts ejecutados desde /tmp"
        )

        cmd = r'''
grep -R "/tmp/" \
/opt /etc /usr/local/bin /var/www \
2>/dev/null
'''

        result = self.run(cmd)

        if result.strip():

            console.print(
                "[red][!] Posibles scripts ejecutados desde /tmp encontrados[/red]"
            )

            print(result)

            self.log(result)

        else:

            console.print(
                "[yellow][-] No se encontraron referencias a /tmp[/yellow]"
            )

            self.log(
                "No se encontraron referencias a /tmp"
            )

    # =========================================
    # ANALYZE
    # =========================================

    def analyze(self):

        checks = [

            (
                "Usuarios",
                "cat /etc/passwd"
            ),

            (
                "Permisos críticos",
                "ls -la /etc/shadow /etc/passwd /etc/sudoers"
            ),

            (
                "Permisos SUDO",
                "sudo -l 2>/dev/null"
            ),

            (
                "Sudoers",
                "cat /etc/sudoers 2>/dev/null; ls -lah /etc/sudoers.d/"
            ),

            (
                "Archivos SUID",
                "find / -perm -4000 2>/dev/null"
            ),

            (
                "Archivos SGID",
                "find / -perm -2000 2>/dev/null"
            ),

            (
                "World writable files",
                "find / -type f -perm -0002 2>/dev/null"
            ),

            (
                "World writable directories",
                "find / -type d -perm -0002 2>/dev/null"
            ),

            (
                "Capabilities",
                "getcap -r / 2>/dev/null"
            ),

            (
                "Cronjobs",
                "ls -lah /etc/cron*; crontab -l 2>/dev/null"
            ),

            (
                "SSH Config",
                "cat /etc/ssh/sshd_config 2>/dev/null | grep -v '^#'"
            ),

            (
                "Docker",
                "docker ps -a 2>/dev/null; id"
            ),

            (
                "Archivos sensibles",
                r'''
find / \
\( \
-name "*.env" -o \
-name "*.txt" -o \
-name "*.conf" -o \
-name "*.bak" -o \
-name "*.sql" -o \
-name "*.pem" -o \
-name "*.key" \
\) 2>/dev/null
'''
            ),

            (
                "Credenciales expuestas",
                r'''
grep -RiE \
"password|passwd|secret|token|apikey|api_key|PRIVATE KEY" \
/home /var/www /opt /etc \
2>/dev/null | head -200
'''
            ),

            (
                "Historiales",
                r'''
find /home -name ".bash_history" 2>/dev/null
'''
            ),

            (
                "Red",
                "ss -tulnp"
            ),

            (
                "Montajes",
                "mount"
            ),

            (
                "NFS y Samba",
                "cat /etc/exports 2>/dev/null; smbstatus 2>/dev/null"
            ),

            (
                "PATH",
                "echo $PATH"
            ),

            (
                "Kernel",
                "uname -a"
            ),

            (
                "Servicios",
                "systemctl list-units --type=service --state=running"
            ),

            (
                "Archivos ejecutables en tmp",
                "find /tmp /var/tmp /dev/shm -type f -executable 2>/dev/null"
            ),

            (
                "Binarios modificables",
                "find /bin /usr/bin /usr/local/bin -writable 2>/dev/null"
            ),

            (
                "Permisos HOME",
                "ls -lah /home"
            )

        ]

        for title, cmd in checks:

            self.execute_check(
                title,
                cmd
            )

        self.tmp_executions()

    # =========================================
    # SAVE REPORT
    # =========================================

    def save_report(self):

        console.print(
            "\n[yellow][?] Nombre del reporte (sin espacios ni símbolos)[/yellow]"
        )

        console.print(
            "[cyan]Ejemplo:[/cyan] reporte_servidor01"
        )

        while True:

            filename = input(
                "\nNombre: "
            ).strip()

            if re.match(
                r'^[a-zA-Z0-9_-]+$',
                filename
            ):

                break

            else:

                console.print(
                    "[red][-] Nombre inválido[/red]"
                )

        final_name = f"{filename}.txt"

        with open(final_name, "w") as f:

            f.write(
                "\n".join(self.report)
            )

        console.print(
            f"\n[green][+] Reporte guardado en {final_name}[/green]"
        )

    # =========================================
    # INTERACTIVE SHELL
    # =========================================

    def interactive_shell(self):

        console.print(
            "\n[yellow][?] ¿Deseas mantener la conexión SSH interactiva? (s/n)[/yellow]"
        )

        choice = input("> ").lower()

        if choice != "s":

            return

        console.print(
            Panel.fit(
                "PASOS RECOMENDADOS PARA TTY",
                style="bold yellow"
            )
        )

        console.print(
            """
[cyan]
1) Ejecutar:
script /dev/null -c bash

2) Presionar:
CTRL + Z

3) En tu terminal local ejecutar:
stty raw -echo; fg

4) Después ejecutar:
reset xterm

5) Finalmente:
export TERM=xterm
export BASH=bash
[/cyan]
"""
        )

        shell = self.client.invoke_shell()

        console.print(
            "\n[green][+] Shell interactiva iniciada[/green]"
        )

        while True:

            command = input(
                f"{self.username}@{self.host}$ "
            )

            if command.lower() in [
                "exit",
                "quit"
            ]:

                break

            shell.send(
                command + "\n"
            )

            time.sleep(1)

            output = shell.recv(
                65535
            ).decode(
                errors="ignore"
            )

            print(output)

    # =========================================
    # CLOSE
    # =========================================

    def close(self):

        if self.client:

            self.client.close()

            console.print(
                "[green][+] Conexión cerrada[/green]"
            )


# =============================================
# MAIN
# =============================================

def main():

    os.system("clear")

    console.print(
    r"""
     ██╗███████╗███████╗ █████╗ ███████╗ ██████╗ 
     ██║██╔════╝██╔════╝██╔══██╗╚══███╔╝██╔═══██╗
     ██║█████╗  █████╗  ███████║  ███╔╝ ██║   ██║
██   ██║██╔══╝  ██╔══╝  ██╔══██║ ███╔╝  ██║   ██║
╚█████╔╝███████╗██║     ██║  ██║███████╗╚██████╔╝
 ╚════╝ ╚══════╝╚═╝     ╚═╝  ╚═╝╚══════╝ ╚═════╝ 
    """,
    style="bold green"
)

    console.print(
        Panel.fit(
            "SSH Linux Security Auditor",
            style="bold red"
        )
    )

    host = input(
        "IP objetivo: "
    )

    username = input(
        "Usuario SSH: "
    )

    password = getpass.getpass(
        "Contraseña SSH: "
    )

    auditor = SSHAudit(
        host,
        username,
        password
    )

    if auditor.connect():

        auditor.analyze()

        auditor.save_report()

        auditor.interactive_shell()

        auditor.close()


if __name__ == "__main__":
    main()
