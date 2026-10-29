import http.server
import socketserver
import threading
import time
import webbrowser
import os
import sys

def main():
    port = 8000
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    web_dir = os.path.join(base_dir, "webxr_app")

    os.chdir(web_dir)

    print("=" * 73)
    print("   WebXR: Пассажирский павильон ж/д станции (ДВГУПС - ЦТИГ)")
    print("   Студент: Болтутин В.В., Группа: БЗИ45ТВР")
    print("=" * 73)
    print()
    print("[1] Локальный адрес для браузера на этом ПК:")
    print(f"    http://localhost:{port}/index.html")
    print()
    print("[2] Для остановки сервера:")
    print("    - Закройте это окно консоли или нажмите [Ctrl + C]")
    print("    - ИЛИ запустите файл: Остановить_WebXR_Сервер.bat")
    print()
    print("=" * 73)
    print()
    print(f"Запуск локального сервера WebXR на порту {port}...")
    print("(Браузер откроется автоматически через 2 секунды)")
    print()

    def open_browser():
        time.sleep(2)
        url = f"http://localhost:{port}/index.html"
        print(f"[OK] Открытие браузера: {url}")
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()

    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("0.0.0.0", port), http.server.SimpleHTTPRequestHandler) as httpd:
            print(f"HTTP сервер активен на порту {port}. Ожидание запросов...\n")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[ИНФО] Сервер остановлен пользователем (Ctrl+C).")
        sys.exit(0)

if __name__ == "__main__":
    main()
