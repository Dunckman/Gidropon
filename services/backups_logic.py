import os
import paramiko
from scp import SCPClient
from django.utils import timezone
from config.settings import BASE_DIR
from dotenv import load_dotenv

def exec_command(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return exit_status, output, error

def make_backup():
    load_dotenv()

    timestamp = timezone.now().date().strftime("%d%m%Y")
    backup_filename = f"backup{timestamp}.sql"

    local_backup_dir = os.path.join(BASE_DIR, "backups")
    os.makedirs(local_backup_dir, exist_ok=True)
    local_path = os.path.join(local_backup_dir, backup_filename)

    remote_backup_dir = os.environ.get("SSH_BACKUP_DIR", "/home/dunckman/gidropon/backups")
    remote_backup_dir = remote_backup_dir.replace('\\', '/')
    remote_file = f"{remote_backup_dir}/{backup_filename}"

    ssh_host = os.environ.get("SSH_HOST", "109.206.142.43")
    ssh_user = os.environ.get("SSH_USER", "dunckman")
    ssh_password = os.environ.get("SSH_PASSWORD", "")
    db_name = os.environ.get("GIDROPON_DB_NAME", "gidropon")
    db_user = os.environ.get("GIDROPON_DB_USER", "postgres")
    db_password = os.environ.get("GIDROPON_DB_PASSWORD", "")
    container = os.environ.get("GIDROPON_CONTAINER_NAME", "gidropon-db")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=ssh_host,
            username=ssh_user,
            password=ssh_password,
            timeout=10,
        )

        # 1. Создаём директорию на сервере
        exec_command(client, f"mkdir -p {remote_backup_dir}")

        # 2. Выполняем pg_dump
        dump_command = (f"docker exec -e PGPASSWORD='{db_password}' {container} "
                        f"pg_dump -U {db_user} {db_name} > {remote_file}")
        status, out, err = exec_command(client, dump_command)

        if status != 0:
            print(f"Ошибка при создании дампа: {err}")
            return

        # 3. Проверяем, что файл создался
        check_command = f"test -s {remote_file}"
        status, out, err = exec_command(client, check_command)
        if status != 0:
            print("Файл бэкапа пустой или не создан")
            return

        print(f"Бэкап на сервере создан: {remote_file}")

        # 4. Копируем локально
        with SCPClient(client.get_transport()) as scp:
            scp.get(remote_file, local_path)
        print(f"Бэкап скопирован локально: {local_path}")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        client.close()