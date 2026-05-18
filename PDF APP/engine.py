import os
import fitz  # PyMuPDF
from PIL import Image
import io

def compress_pdf(input_path, output_path, dpi=95, quality=40):
    """
    Motor definitivo para PDFs escaneados:
    - Renderiza cada página con PyMuPDF
    - Re-comprime la imagen con Pillow (control total de calidad JPEG)
    - Reconstruye el PDF completo con páginas livianas
    """
    try:
        src = fitz.open(input_path)
        out = fitz.open()
        total_pages = len(src)

        print(f"Procesando {total_pages} páginas a {dpi} DPI, calidad JPEG {quality}%...")

        for i, page in enumerate(src):
            # 1. Renderizar la página como imagen cruda usando PyMuPDF
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            # 2. Convertir a imagen Pillow (control total sobre compresión)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # 3. Comprimir como JPEG con calidad controlada
            jpeg_buffer = io.BytesIO()
            img.save(jpeg_buffer, format="JPEG", quality=quality, optimize=True)
            jpeg_bytes = jpeg_buffer.getvalue()

            # 4. Insertar la imagen comprimida en una nueva página PDF
            new_page = out.new_page(width=page.rect.width, height=page.rect.height)
            new_page.insert_image(new_page.rect, stream=jpeg_bytes)

            if (i + 1) % 50 == 0 or (i + 1) == total_pages:
                print(f"  {i + 1}/{total_pages} páginas procesadas...")

        # 5. Guardar con limpieza de estructura
        out.save(output_path, garbage=4, deflate=True, clean=True)
        src.close()
        out.close()

        final_size = os.path.getsize(output_path) / (1024 * 1024)
        original_size = os.path.getsize(input_path) / (1024 * 1024)
        reduction = ((original_size - final_size) / original_size) * 100
        print(f"✓ Completado: {original_size:.1f} MB → {final_size:.2f} MB ({reduction:.0f}% reducción)")
        return True

    except Exception as e:
        print(f"Error en compresión: {e}")
        return False


def find_large_pdfs(directory, min_size_mb=30, socketio=None):
    large_files = []
    if not os.path.exists(directory):
        return []

    for root, dirs, files in os.walk(directory):
        if socketio:
            socketio.emit('scan_progress', {'folder': root})
            socketio.sleep(0)

        for file in files:
            if file.lower().endswith('.pdf') and "_optimizado" not in file.lower():
                path = os.path.join(root, file)
                try:
                    size_mb = os.path.getsize(path) / (1024 * 1024)
                    if size_mb > min_size_mb:
                        large_files.append({
                            "name": file, "path": path, "size": round(size_mb, 2)
                        })
                except:
                    continue
    return large_files
