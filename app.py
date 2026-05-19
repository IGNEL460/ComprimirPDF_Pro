from flask import Flask, render_template_string, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
import os, sys, threading, webbrowser
import engine
import tkinter as tk
from tkinter import filedialog

def resource_path(relative_path):
    """ Obtiene la ruta absoluta para recursos, compatible con PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Ruta inicial por defecto
current_config = {"path": r"\\server-ii\Control-Interno"}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Compressor Pro - Enterprise</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: 'Inter', sans-serif; background: #0f172a; color: #f8fafc; }
        .glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); }
        .accent-gradient { background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); }
    </style>
    <!-- Favicon -->
    <link rel="apple-touch-icon" sizes="180x180" href="/static/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/static/favicon-16x16.png">
</head>
<body class="min-h-screen p-8">
    <div class="max-w-4xl mx-auto">
        <header class="mb-8 flex justify-between items-end">
            <div>
                <h1 class="text-3xl font-bold text-indigo-400">PDF Compressor Pro</h1>
                <p class="text-slate-400 text-sm">Ruta activa: <span id="path-display" class="text-slate-200 font-mono text-[10px]"> {{ server_path }} </span></p>
            </div>
            <button onclick="selectFolder()" class="bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 border border-white/5">
                📂 Seleccionar Carpeta
            </button>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <button onclick="scan()" id="scan-btn" class="accent-gradient p-4 rounded-xl font-bold shadow-lg shadow-indigo-500/20 hover:scale-[1.02] transition-all">
                Iniciar Búsqueda en Carpeta
            </button>
            <div class="glass p-4 rounded-xl flex items-center justify-between">
                <div>
                    <span id="count" class="text-3xl font-bold text-indigo-400">0</span>
                    <p class="text-[10px] text-slate-500 uppercase font-bold">PDFs Detectados</p>
                </div>
                <div id="status-icon" class="hidden">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-400"></div>
                </div>
            </div>
        </div>

        <div id="scan-feedback" class="hidden mb-8 glass p-6 rounded-xl border-l-4 border-indigo-500">
            <div class="flex items-center gap-3 mb-2">
                <div class="animate-bounce text-indigo-400 font-black text-sm">🔍</div>
                <div class="text-xs font-bold text-slate-200 uppercase tracking-tighter">Escaneando directorio...</div>
            </div>
            <div class="bg-black/30 p-3 rounded font-mono text-[9px] text-indigo-300 truncate" id="current-folder">
                Esperando señal...
            </div>
        </div>

        <div class="glass rounded-3xl overflow-hidden shadow-2xl">
            <div class="p-4 bg-slate-800/50 border-b border-white/5">
                <h3 class="text-xs font-bold uppercase tracking-widest text-slate-400">Archivos encontrados (>30MB)</h3>
            </div>
            <div class="max-h-[500px] overflow-y-auto scrollbar-hide">
                <table class="w-full text-left">
                    <thead class="bg-slate-900/80 sticky top-0">
                        <tr>
                            <th class="p-4 text-[10px] font-black text-slate-500 uppercase">Ubicación / Archivo</th>
                            <th class="p-4 text-[10px] font-black text-slate-500 uppercase w-24 text-center">Peso</th>
                            <th class="p-4 text-[10px] font-black text-slate-500 uppercase text-right w-32">Acción</th>
                        </tr>
                    </thead>
                    <tbody id="list" class="divide-y divide-white/5">
                        <tr><td colspan="3" class="p-20 text-center text-slate-600 italic text-sm">Selecciona una carpeta y corre el escaneo.</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let currentPath = "{{ server_path }}";

        socket.on('scan_progress', (data) => {
            document.getElementById('current-folder').innerText = data.folder;
        });

        async function selectFolder() {
            try {
                const res = await fetch('/api/select_folder');
                const data = await res.json();
                if(data.path) {
                    currentPath = data.path;
                    document.getElementById('path-display').innerText = data.path;
                }
            } catch(e) { console.error(e); }
        }

        async function scan() {
            const btn = document.getElementById('scan-btn');
            const list = document.getElementById('list');
            const feedback = document.getElementById('scan-feedback');
            const statusIcon = document.getElementById('status-icon');
            const countLabel = document.getElementById('count');
            
            btn.disabled = true; btn.classList.add('opacity-50');
            feedback.classList.remove('hidden');
            statusIcon.classList.remove('hidden');
            list.innerHTML = '';
            countLabel.innerText = "0";

            try {
                const res = await fetch('/api/scan', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({path: currentPath})
                });
                const data = await res.json();
                
                statusIcon.classList.add('hidden');
                feedback.classList.add('hidden');
                
                if(data.files && data.files.length > 0) {
                    countLabel.innerText = data.files.length;
                    list.innerHTML = data.files.map((f, i) => `
                        <tr class="hover:bg-indigo-500/5 group text-xs">
                            <td class="p-4">
                                <div class="text-[9px] text-slate-600 truncate max-w-sm mb-1 group-hover:text-slate-400 font-mono">${f.path}</div>
                                <div class="font-bold text-slate-100 break-all leading-tight pr-4">${f.name}</div>
                            </td>
                            <td class="p-4 text-center">
                                <span class="bg-indigo-500/10 text-indigo-400 font-bold px-2 py-1 rounded border border-indigo-500/20">
                                    ${f.size} MB
                                </span>
                            </td>
                            <td class="p-4 text-right">
                                <button id="btn-${i}" onclick="compress(${i}, '${f.path.replace(/\\\\/g, '\\\\\\\\')}')" 
                                    class="text-indigo-400 font-black uppercase border border-indigo-500/30 px-3 py-2 rounded-lg hover:bg-indigo-500 hover:text-white transition-all text-[10px]">
                                    Comprimir
                                </button>
                            </td>
                        </tr>
                    `).join('');
                } else {
                    list.innerHTML = '<tr><td colspan="3" class="p-20 text-center text-slate-500 italic">No se hallaron archivos pesados en esta carpeta.</td></tr>';
                }
            } catch(e) {
                list.innerHTML = '<tr><td colspan="3" class="p-20 text-center text-red-500 font-bold">Error en la comunicación con el servidor local.</td></tr>';
            } finally {
                btn.disabled = false; btn.classList.remove('opacity-50');
            }
        }

        async function compress(id, path) {
            const btn = document.getElementById('btn-'+id);
            btn.innerText = "PROCESANDO...";
            btn.disabled = true;
            
            const res = await fetch('/api/compress', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({path})
            });
            const data = await res.json();
            if(data.success) {
                btn.innerText = "✓ LISTO";
                btn.className = "text-green-400 font-bold text-[10px]";
            } else {
                btn.innerText = "ERROR";
                btn.className = "text-red-400 font-bold text-[10px]";
                btn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, server_path=current_config["path"])

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(resource_path('favicon_io (1)'), filename)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(resource_path('favicon_io (1)'), 'favicon.ico')

@app.route('/api/select_folder')
def select_folder():
    # Creamos una ventana de Tkinter oculta para el explorador nativo
    root = tk.Tk()
    root.withdraw()
    # Forzamos a que esté al frente
    root.attributes('-topmost', True)
    path = filedialog.askdirectory(initialdir=current_config["path"], title="Seleccionar Carpeta para Escanear")
    root.destroy()
    
    if path:
        current_config["path"] = path.replace('/', '\\')
        return jsonify({"path": current_config["path"]})
    return jsonify({"path": None})

@app.route('/api/scan', methods=['POST'])
def scan():
    path = request.json.get('path', current_config["path"])
    files = engine.find_large_pdfs(path, socketio=socketio)
    return jsonify({"files": files})

@app.route('/api/compress', methods=['POST'])
def compress():
    path = request.json.get('path')
    output = path.replace(".pdf", "_optimizado.pdf")
    success = engine.compress_pdf(path, output)
    return jsonify({"success": success})

if __name__ == '__main__':
    # Abrir el navegador automaticamente luego de que el servidor arranque
    def abrir_navegador():
        import time
        time.sleep(1.5)
        webbrowser.open('http://localhost:5000')

    t = threading.Thread(target=abrir_navegador, daemon=True)
    t.start()

    socketio.run(app, host='127.0.0.1', port=5000, allow_unsafe_werkzeug=True)
