# SSH Linux Security Auditor

Auditoría avanzada de seguridad Linux por SSH orientada a:

- Enumeración defensiva
- Revisión de malas configuraciones
- Hardening
- Detección de riesgos
- Identificación de vectores de escalada de privilegios
- Detección de movimiento lateral
- Auditoría de permisos inseguros

---

# Descripción

SSH Linux Security Auditor es una herramienta desarrollada en Python que permite conectarse por SSH a un sistema Linux remoto y realizar una auditoría automatizada de seguridad.

La herramienta enumera configuraciones inseguras, permisos peligrosos, archivos sensibles, servicios vulnerables y múltiples indicadores que podrían permitir:

- Escalada de privilegios
- Persistencia
- Movimiento lateral
- Exposición de credenciales
- Ejecución insegura de scripts
- Abuso de sudo
- Exposición de secretos

Todo el resultado puede exportarse automáticamente a un reporte `.txt`.

---

# Características

## Enumeración avanzada

La herramienta analiza:

### Usuarios

- `/etc/passwd`
- Usuarios del sistema
- Cuentas sin password

---

### Permisos críticos

- `/etc/shadow`
- `/etc/sudoers`
- `/etc/passwd`

---

### SUDO

- `sudo -l`
- Reglas sudo
- Archivos en `/etc/sudoers.d`

---

### Archivos SUID y SGID

Detección automática de:

- Binarios SUID
- Binarios SGID

---

### World Writable

Detección de:

- Archivos escribibles globalmente
- Directorios escribibles globalmente

---

### Capabilities

Análisis de:

```bash
getcap -r /
```

---

### Cronjobs

Revisión de:

- `/etc/cron*`
- Crontabs
- Tareas programadas

---

### SSH

Enumeración de:

- Configuración SSH
- Parámetros inseguros
- Configuración expuesta

---

### Docker

Detección de:

- Contenedores
- Permisos Docker
- Posible Docker breakout

---

### Archivos sensibles

Búsqueda de:

- `.env`
- `.txt`
- `.sql`
- `.pem`
- `.key`
- `.conf`
- `.bak`

---

### Credenciales expuestas

Detección de:

- passwords
- secrets
- tokens
- api keys
- private keys

---

### Historiales

Enumeración de:

- `.bash_history`

---

### Red

Detección de:

- Servicios abiertos
- Conexiones activas
- Puertos en escucha

---

### NFS / Samba

Enumeración de:

- Recursos exportados
- Comparticiones

---

### PATH Hijacking

Detección de:

- PATH inseguros
- Variables peligrosas

---

### Servicios

Enumeración de:

- Servicios activos
- Systemd

---

### Scripts ejecutados desde /tmp

La herramienta busca scripts inseguros que ejecuten archivos desde:

```bash
/tmp
```

Ejemplo:

```bash
/opt/script.sh -> /tmp/run.sh
```

Esto puede permitir:

- Escalada de privilegios
- Persistencia
- Ejecución arbitraria

---

### Binarios modificables

Detección de:

- Binarios escribibles
- Posibles reemplazos maliciosos

---

# Requisitos

## Python

Python 3.10 o superior recomendado.

---

## Dependencias

Instalar:

```bash
pip install paramiko rich
```

---

# Instalación

## Clonar repositorio

```bash
git clone https://github.com/Alejandro609x/Auditoria_SSH.git
```
---

## Entrar al proyecto

```bash
cd Auditoria_SSH
```

## Entrar al Script
```bash
cd Analizador_SSH
```
---

# Ejecución

Dar permisos:

```bash
chmod +x ssh_audit.py
```

Ejecutar:

```bash
python3 ssh_audit.py
```
---

# Uso

Al iniciar la herramienta solicitará:

```text
IP objetivo
Usuario SSH
Contraseña SSH
```

Posteriormente comenzará automáticamente la auditoría.

---

# Reporte TXT

Al finalizar el análisis solicitará un nombre para guardar el reporte.

Ejemplo:

```text
reporte_servidor01
```

El archivo generado será:

```text
reporte_servidor01.txt
```
![Target](/Analizador_SSH/Imagenes/nombre.png)

---

# Shell interactiva

Después del análisis puede mantenerse la conexión SSH interactiva.

La herramienta mostrará recomendaciones para realizar tratamiento TTY.

![Target](/Analizador_SSH/Imagenes/sesionssh.png)

---

# Tratamiento TTY recomendado

La herramienta mostrará automáticamente:

```bash
script /dev/null -c bash
```

Luego:

```bash
CTRL + Z
```

En terminal local:

```bash
stty raw -echo; fg
```

Después:

```bash
reset xterm
```

Finalmente:

```bash
export TERM=xterm
export BASH=bash
```

---

# Ejemplo de uso

```bash
python3 ssh_audit.py
```

Salida:

![Target](/Analizador_SSH/Imagenes/primero.png)

---

# Qué puede detectar

## Riesgos críticos

- Binarios SUID peligrosos
- Capabilities explotables
- Credenciales hardcodeadas
- Docker breakout
- Cronjobs inseguros
- PATH hijacking
- SSH inseguro
- World writable
- Scripts ejecutados desde /tmp
- Binarios modificables
- Tokens expuestos
- Secrets expuestos

![Target](/Analizador_SSH/Imagenes/segundo.png)

![Target](/Analizador_SSH/Imagenes/tercero.png)

![Target](/Analizador_SSH/Imagenes/cuatro.png)

![Target](/Analizador_SSH/Imagenes/cinco.png)


---

# Casos reales detectables

## Script vulnerable

```bash
/opt/backup.sh
```

Contenido:

```bash
bash /tmp/run.sh
```

Si `/tmp` es escribible:

```bash
chmod 777 /tmp
```

Un atacante podría reemplazar:

```bash
/tmp/run.sh
```

Y obtener:

- ejecución arbitraria
- persistencia
- escalada de privilegios

La herramienta detecta automáticamente este patrón.

---

# Limitaciones

La herramienta:

- NO explota vulnerabilidades
- NO modifica configuraciones
- NO realiza persistencia
- NO ejecuta payloads
- NO altera el sistema

Está orientada únicamente a:

- auditoría
- enumeración
- análisis defensivo

---

# Recomendaciones

## Ejecutar con permisos mínimos

No utilizar root salvo necesidad específica.

---

## Revisar especialmente

```text
/etc/sudoers
/etc/passwd
/etc/shadow
/opt
/tmp
/var/tmp
/dev/shm
/home
/var/www
```

---

# Seguridad

Usar únicamente en:

- sistemas propios
- laboratorios
- entornos autorizados
- auditorías permitidas

El uso no autorizado puede ser ilegal.

---

# Disclaimer

Esta herramienta se proporciona únicamente con fines educativos y de auditoría autorizada.

El autor no se hace responsable del uso indebido de la herramienta.
