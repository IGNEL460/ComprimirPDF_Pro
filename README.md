# PDF Compressor Pro

Aplicación de compresión de archivos PDF diseñada para optimizar documentos pesados (superiores a 30MB) manteniéndolos en una calidad óptima y legible. Desarrollada para uso interno.

## Tecnologías Utilizadas

- **Python 3**
- **Flask & Flask-SocketIO**: Para la interfaz web de usuario y websockets en tiempo real.
- **PyMuPDF (fitz) y Pillow**: Motores de renderizado y compresión interna del PDF.
- **Tailwind CSS**: Interfaz de usuario estilizada.

## Uso del Ejecutable (Recomendado para usuarios sin Python)

Simplemente descarga la versión compilada desde la sección [Releases](https://github.com/) de este repositorio, o compila el tuyo ejecutando el archivo `Crear_Ejecutable.bat`.

## Instalación desde Código Fuente

Si deseas ejecutar la herramienta localmente usando Python:

1. Clona el repositorio.
2. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta la aplicación:
   ```bash
   python app.py
   ```
4. Se abrirá automáticamente la interfaz web en tu navegador en `http://localhost:5000`.

## Compilar el Ejecutable

Si deseas generar el archivo `.exe` tú mismo, puedes utilizar el script proporcionado:
```bash
Crear_Ejecutable.bat
```
El archivo resultante se guardará en la carpeta `dist`.

## Seguridad y Privacidad
El archivo `.gitignore` está configurado para omitir la carga accidental de archivos sensibles `.pdf`, `.log` y las carpetas de compilación.
