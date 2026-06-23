"""
Launcher do Acai Stock - versao .exe.

Inicia o servidor Django, abre o navegador e mantem rodando.
Cria o banco de dados SQLite automaticamente na primeira execucao.
"""
import os
import sys
import subprocess
import time
import threading
import webbrowser


def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(relative):
    """Caminho para recursos empacotados pelo PyInstaller."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative)


def setup_environment():
    base_dir = get_base_dir()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.portable")
    os.environ["ACAI_BASE_DIR"] = base_dir

    # Criar .env minimo se nao existir
    env_path = os.path.join(base_dir, ".env")
    if not os.path.exists(env_path):
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("""SECRET_KEY=exe-portable-key-change-me
DEBUG=True
ALLOWED_HOSTS=*
CELERY_BROKER_URL=memory://
CELERY_RESULT_BACKEND=cache+memory://
DEFAULT_FROM_EMAIL=suporte@acaistock.com
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
""")


def run_migrations():
    from django.core.management import call_command
    call_command("migrate", verbosity=0, interactive=False)


def collect_static():
    from django.core.management import call_command
    call_command("collectstatic", verbosity=0, interactive=False)


def create_superuser():
    from accounts.models import User
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@acaiteria.com",
            password="Admin123!",
        )
        u = User.objects.get(username="admin")
        u.role = "superadmin"
        u.save()


def open_browser_delayed():
    time.sleep(3)
    webbrowser.open("http://127.0.0.1:8000/")


def main():
    print("=" * 50)
    print("  Acai Stock - Sistema de Gestao de Estoque")
    print("=" * 50)
    print()

    setup_environment()

    print("[1/4] Inicializando Django...")
    import django
    django.setup()

    print("[2/4] Criando banco de dados (SQLite)...")
    run_migrations()

    print("[3/4] Coletando arquivos estaticos...")
    collect_static()

    print("[4/4] Criando usuario administrador...")
    create_superuser()

    print()
    print("  Login: admin")
    print("  Senha: Admin123!")
    print()
    print("  Acesse: http://127.0.0.1:8000/")
    print("  Admin:  http://127.0.0.1:8000/admin/")
    print()
    print("  Pressione Ctrl+C para parar o servidor.")
    print()

    # Abrir browser apos 3 segundos
    threading.Thread(target=open_browser_delayed, daemon=True).start()

    # Iniciar servidor
    from django.core.management import call_command
    call_command("runserver", "127.0.0.1:8000", "--noreload", verbosity=1)


if __name__ == "__main__":
    main()
