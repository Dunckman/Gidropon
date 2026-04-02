import os
import paramiko
import subprocess
from scp import SCPClient
from django.utils import timezone
from config.settings import BASE_DIR
from dotenv import load_dotenv

TIMESTAMP_FORMAT = "%Y%m%d"

def exec_command(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return exit_status, output, error

def make_backup_server(is_task=False):
    load_dotenv()

    timestamp = timezone.now().date().strftime(TIMESTAMP_FORMAT)
    backup_filename = f"backup{timestamp}.sql"

    local_backup_dir = os.path.join(BASE_DIR, "backups")
    os.makedirs(local_backup_dir, exist_ok=True)
    local_path = os.path.join(local_backup_dir, backup_filename)

    remote_backup_dir = os.environ.get("SSH_BACKUP_DIR", "/home/dunckman/gidropon/backups")
    remote_backup_dir = remote_backup_dir.replace('\\', '/')
    remote_file = f"{remote_backup_dir}/{backup_filename}"

    ssh_host = os.environ.get("SSH_HOST", "localhost")
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
            print(f"Ошибка при создании дампа: {err}.")
            return

        # 3. Проверяем, что файл создался
        check_command = f"test -s {remote_file}"
        status, out, err = exec_command(client, check_command)
        if status != 0:
            print("Файл бэкапа пустой или не создан.")
            return

        if not is_task:
            print(f"Бэкап на сервере создан: {remote_file}.")

        # 4. Копируем локально
        with SCPClient(client.get_transport()) as scp:
            scp.get(remote_file, local_path)

        if not is_task:
            print(f"Бэкап скопирован локально: {local_path}.")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        client.close()


def make_backup_local(is_task=False):
    load_dotenv()

    timestamp = timezone.now().date().strftime(TIMESTAMP_FORMAT)
    backup_filename = f"backup{timestamp}.sql"

    local_backup_dir = os.path.join(BASE_DIR, "backups")
    os.makedirs(local_backup_dir, exist_ok=True)
    local_path = os.path.join(local_backup_dir, backup_filename)

    remote_backup_dir = os.environ.get("SSH_BACKUP_DIR", "/home/dunckman/gidropon/backups")
    remote_backup_dir = remote_backup_dir.replace('\\', '/')
    remote_file = f"{remote_backup_dir}/{backup_filename}"

    ssh_host = os.environ.get("SSH_HOST")
    ssh_user = os.environ.get("SSH_USER")
    ssh_password = os.environ.get("SSH_PASSWORD")

    # DB Config
    db_name = os.environ.get("GIDROPON_DB_NAME", "gidropon")
    db_user = os.environ.get("GIDROPON_DB_USER", "postgres")
    db_password = os.environ.get("GIDROPON_DB_PASSWORD", "")
    container = os.environ.get("GIDROPON_CONTAINER_NAME", "gidropon-db")
    use_docker = os.environ.get("USE_DOCKER_LOCAL", "False").lower() == "true"

    # 1. Создаём бэкап ЛОКАЛЬНО
    try:
        dump_command = (
            f"docker exec -e PGPASSWORD={db_password} {container} "
            f"pg_dump -U {db_user} {db_name}"
        )

        # Запуск процесса
        with open(local_path, 'w', encoding='utf-8') as f:
            env = os.environ.copy()
            if not use_docker:
                env['PGPASSWORD'] = db_password

            process = subprocess.Popen(
                dump_command,
                stdout=f,
                stderr=subprocess.PIPE,
                env=env,
                shell=False
            )
            _, stderr = process.communicate()

            if process.returncode != 0:
                err_text = stderr.decode('utf-8', errors='ignore')
                print(f"Ошибка команды pg_dump: {err_text}.")
                # Не удаляем файл сразу, чтобы можно было проверить
                return

        if os.path.getsize(local_path) == 0:
            print("Бэкап пустой.")
            return

        if not is_task:
            print(f"Бэкап сохранён локально: {local_path}.")

    except Exception as e:
        print(f"Ошибка создания локального бэкапа: {e}.")
        return

    # 2. Копируем бэкап на удалённый сервер
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=ssh_host,
            username=ssh_user,
            password=ssh_password,
            timeout=10,
        )

        exec_command(client, f"mkdir -p {remote_backup_dir}")

        with SCPClient(client.get_transport()) as scp:
            scp.put(local_path, remote_file)

        if not is_task:
            print(f"Бэкап скопирован на сервер: {remote_file}.")

    except Exception as e:
        print(f"Ошибка копирования бэкапа на сервер: {e}.")
    finally:
        client.close()