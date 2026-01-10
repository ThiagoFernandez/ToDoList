# To-Do List con Notificaciones por Email y Cifrado

Aplicación de gestión de tareas por consola desarrollada en **Python**, orientada a la organización personal mediante tareas **diarias, semanales, mensuales y anuales**, integrando la **Matriz de Eisenhower**, persistencia en archivos JSON, cifrado de información sensible y notificaciones automáticas por email.

---

## Objetivo del proyecto

El objetivo de este proyecto es aplicar **fundamentos sólidos de programación en Python**:
- estructuras de datos
- control de flujo
- manejo de errores
- persistencia
- seguridad básica
- automatización

Todo dentro de una aplicación funcional, extensible y ejecutable desde consola.

---

## Funcionalidades principales

- Registro y login de usuarios
- Hash de contraseñas con **SHA-256**
- Gestión completa de tareas (CRUD):
  - diarias
  - semanales
  - mensuales
  - anuales
- Estados de tareas:
  - Done
  - In progress
  - Canceled
  - Postponed
  - Need review
- Clasificación por **Matriz de Eisenhower**
- Cifrado de descripciones sensibles
- Persistencia en archivos JSON
- Notificaciones automáticas por **email**
- Configuración granular de notificaciones por tipo de tarea
- Sistema de flags y control de fechas para evitar envíos duplicados

---

## Seguridad

- Las contraseñas se almacenan **hasheadas** utilizando `hashlib.sha256`
- Las descripciones de las tareas se almacenan **cifradas** mediante **Fernet (cryptography)**
- La clave de cifrado se guarda en un archivo local (`secret.key`)

---

## Persistencia de datos

El sistema utiliza archivos JSON como base de datos local:

- `task_list.json`  
  Almacena usuarios, contraseñas y tareas.
- `notificationSettings.json`  
  Almacena configuración de notificaciones, emails y fechas de ejecución.
- `secret.key`  
  Clave simétrica utilizada para cifrado y descifrado.

La aplicación es capaz de **crear automáticamente los archivos** si no existen.

---

## Sistema de notificaciones

- Envío automático de reportes de tareas pendientes por email
- Configuración independiente por:
  - daily
  - weekly
  - monthly
  - yearly
- Control de ejecución mediante:
  - fecha/hora configurada por el usuario
  - campo `next_run` para evitar reenvíos
- El envío solo ocurre cuando corresponde según la fecha actual

---

## Tecnologías y librerías utilizadas

- Python 3.10+
- `json`
- `hashlib`
- `pwinput`
- `cryptography (Fernet)`
- `smtplib`
- `email.message`
- `datetime`
- `email_validator`

---

## Ejecución del programa

1. Clonar el repositorio
2. Instalar dependencias necesarias:
    a. pip install email.message
    b. pip install cryptography.fernet 
    c. pip install datetime
    d. pip install email_validator
3. Ejecutar:

```bash
python main.py
