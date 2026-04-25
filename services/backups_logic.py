import os
import subprocess

import paramiko
from django.utils import timezone
from dotenv import load_dotenv
from scp import SCPClient

from config.settings import BASE_DIR

TIMESTAMP_FORMAT = "%Y%m%d"


def _is_running_in_docker():
    return os.path.exists("/.dockerenv") or os.environ.get("RUNNING_IN_DOCKER", "").lower() == "true"


def _build_db_targets(default_host, default_port):
    host = (default_host or "").strip()
    port = str(default_port or "").strip() or "5432"
    in_docker = _is_running_in_docker()

    targets = [(host, port)]

    localhost_aliases = {"localhost", "127.0.0.1"}
    docker_aliases = {"db", "postgres", "postgresql"}

    if in_docker and (host in localhost_aliases or not host):
        targets.append(("db", "5432"))

    if (not in_docker) and host in docker_aliases:
        targets.append(("localhost", os.environ.get("LOCAL_DB_PORT", "5437")))

    unique_targets = []
    seen = set()
    for target in targets:
        if target in seen:
            continue
        seen.add(target)
        unique_targets.append(target)

    return unique_targets


def _run_dump_command(command, local_path, env):
    with open(local_path, "w", encoding="utf-8") as file_handle:
        process = subprocess.run(
            command,
            stdout=file_handle,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )

    stderr_text = process.stderr.decode("utf-8", errors="ignore").strip()
    ok = process.returncode == 0 and os.path.exists(local_path) and os.path.getsize(local_path) > 0
    return ok, stderr_text


def exec_command(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode("utf-8")
    error = stderr.read().decode("utf-8")
    return exit_status, output, error


def make_backup(is_task=False):
    load_dotenv()

    timestamp = timezone.now().date().strftime(TIMESTAMP_FORMAT)
    backup_filename = f"backup{timestamp}.sql"

    local_backup_dir = os.path.join(BASE_DIR, "backups")
    os.makedirs(local_backup_dir, exist_ok=True)
    local_path = os.path.join(local_backup_dir, backup_filename)

    remote_backup_dir = os.environ.get("SSH_BACKUP_DIR", "/home/dunckman/gidropon/backups")
    remote_backup_dir = remote_backup_dir.replace("\\", "/")
    remote_file = f"{remote_backup_dir}/{backup_filename}"

    ssh_host = os.environ.get("SSH_HOST")
    ssh_user = os.environ.get("SSH_USER")
    ssh_password = os.environ.get("SSH_PASSWORD")

    db_name = os.environ.get("GIDROPON_DB_NAME", "gidropon")
    db_user = os.environ.get("GIDROPON_DB_USER", "postgres")
    db_password = os.environ.get("GIDROPON_DB_PASSWORD", "")
    db_host = os.environ.get("GIDROPON_DB_HOST", "localhost")
    db_port = os.environ.get("GIDROPON_DB_PORT", "5432")
    db_container = os.environ.get("GIDROPON_CONTAINER_NAME", "gidropon-db")

    db_targets = _build_db_targets(db_host, db_port)

    try:
        env = os.environ.copy()
        env["PGPASSWORD"] = db_password

        dump_errors = []
        dump_succeeded = False
        used_target = None
        pg_dump_missing = False

        for host, port in db_targets:
            native_cmd = [
                "pg_dump",
                "-h", host,
                "-p", str(port),
                "-U", db_user,
                db_name,
            ]
            try:
                ok, err_text = _run_dump_command(native_cmd, local_path, env)
                if ok:
                    dump_succeeded = True
                    used_target = (host, port)
                    break
                dump_errors.append(f"{host}:{port} -> {err_text or 'unknown error'}")
            except FileNotFoundError:
                pg_dump_missing = True
                break

        # Host fallback: if native pg_dump failed (or is missing), try old docker exec flow.
        if not dump_succeeded:
            docker_cmd = [
                "docker",
                "exec",
                "-e",
                f"PGPASSWORD={db_password}",
                db_container,
                "pg_dump",
                "-U",
                db_user,
                db_name,
            ]
            try:
                ok, err_text = _run_dump_command(docker_cmd, local_path, env)
                if ok:
                    dump_succeeded = True
                    used_target = (f"docker:{db_container}", "internal")
                else:
                    dump_errors.append(f"docker exec ({db_container}) -> {err_text or 'unknown error'}")
            except FileNotFoundError:
                if pg_dump_missing:
                    dump_errors.append("pg_dump not found and docker CLI not found in current environment")
                else:
                    dump_errors.append("docker CLI not found in current environment")

        if not dump_succeeded:
            print("Ошибка команды pg_dump. Попытки: " + "; ".join(dump_errors) + ".")
            return

        if not is_task and used_target is not None:
            print(f"pg_dump выполнен через {used_target[0]}:{used_target[1]}.")

        if os.path.getsize(local_path) == 0:
            print("Бэкап пустой.")
            return

        if not is_task:
            print(f"Бэкап сохранён локально: {local_path}.")

    except Exception as exc:
        print(f"Ошибка создания локального бэкапа: {exc}.")
        return

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

    except Exception as exc:
        print(f"Ошибка копирования бэкапа на сервер: {exc}.")
    finally:
        client.close()
