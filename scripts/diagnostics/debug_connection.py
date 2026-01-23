import json
import socket
import subprocess
import time

LOG_PATH = "/home/evan/Documents/Projects/FightSFTickets/.cursor/debug.log"
SESSION_ID = "debug-session"
RUN_ID = "run1"


def log_event(hypothesis_id, location, message, data):
    entry = {
        "sessionId": SESSION_ID,
        "runId": RUN_ID,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(entry) + "\n")


def run_cmd(cmd, timeout=8):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        output = (result.stdout or "").strip()
        return {"code": result.returncode, "output": output[:2000]}
    except subprocess.TimeoutExpired as exc:
        return {"code": "timeout", "output": str(exc)[:2000]}
    except Exception as exc:  # noqa: BLE001
        return {"code": "error", "output": str(exc)}


def test_socket(host, port, timeout=3):
    start = time.time()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return {"status": "connected", "ms": int((time.time() - start) * 1000)}
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "error",
            "error": type(exc).__name__,
            "message": str(exc),
            "ms": int((time.time() - start) * 1000),
        }


def main():
    # region agent log
    log_event(
        "A",
        "scripts/diagnostics/debug_connection.py:41",
        "starting diagnostics",
        {"cwd": run_cmd("pwd")},
    )
    # endregion

    # region agent log
    log_event(
        "A",
        "scripts/diagnostics/debug_connection.py:50",
        "docker compose ps",
        run_cmd("cd /home/evan/Documents/Projects/FightSFTickets && sudo docker compose ps"),
    )
    # endregion

    # region agent log
    log_event(
        "B",
        "scripts/diagnostics/debug_connection.py:59",
        "socket connect 127.0.0.1:80",
        test_socket("127.0.0.1", 80),
    )
    # endregion

    # region agent log
    log_event(
        "B",
        "scripts/diagnostics/debug_connection.py:68",
        "socket connect 127.0.0.1:3000",
        test_socket("127.0.0.1", 3000),
    )
    # endregion

    # region agent log
    log_event(
        "E",
        "scripts/diagnostics/debug_connection.py:77",
        "curl host 127.0.0.1:80",
        run_cmd("curl -4 -v http://127.0.0.1:80 2>&1 | head -40"),
    )
    # endregion

    # region agent log
    log_event(
        "E",
        "scripts/diagnostics/debug_connection.py:86",
        "curl host 127.0.0.1:3000",
        run_cmd("curl -4 -v http://127.0.0.1:3000 2>&1 | head -40"),
    )
    # endregion

    # region agent log
    log_event(
        "F",
        "scripts/diagnostics/debug_connection.py:95",
        "nginx to web from container",
        run_cmd(
            "cd /home/evan/Documents/Projects/FightSFTickets && "
            "sudo docker compose exec -T nginx wget -qO- http://web:3000 2>&1 | head -5",
            timeout=8,
        ),
    )
    # endregion

    # region agent log
    log_event(
        "F",
        "scripts/diagnostics/debug_connection.py:106",
        "web container local request",
        run_cmd(
            "cd /home/evan/Documents/Projects/FightSFTickets && "
            "sudo docker compose exec -T web wget -qO- http://localhost:3000 2>&1 | head -5",
            timeout=8,
        ),
    )
    # endregion

    # region agent log
    log_event(
        "H",
        "scripts/diagnostics/debug_connection.py:117",
        "docker inspect container IPs",
        run_cmd(
            "cd /home/evan/Documents/Projects/FightSFTickets && "
            "sudo docker inspect -f '{{.Name}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "
            "fightsftickets-web-1 fightsftickets-nginx-1 fightsftickets-api-1",
            timeout=8,
        ),
    )
    # endregion

    # region agent log
    log_event(
        "H",
        "scripts/diagnostics/debug_connection.py:130",
        "curl host to web container IP",
        run_cmd(
            "WEB_IP=$(sudo docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' fightsftickets-web-1) && "
            "curl -4 -v http://$WEB_IP:3000 2>&1 | head -40",
            timeout=8,
        ),
    )
    # endregion

    # region agent log
    log_event(
        "I",
        "scripts/diagnostics/debug_connection.py:141",
        "web container listen sockets",
        run_cmd(
            "cd /home/evan/Documents/Projects/FightSFTickets && "
            "sudo docker compose exec -T web sh -lc \"ss -tlnp | grep 3000 || netstat -tlnp | grep 3000\"",
            timeout=8,
        ),
    )
    # endregion

    # region agent log
    log_event(
        "I",
        "scripts/diagnostics/debug_connection.py:152",
        "web container env host vars",
        run_cmd(
            "cd /home/evan/Documents/Projects/FightSFTickets && "
            "sudo docker compose exec -T web sh -lc \"env | grep -E 'HOST|PORT|NEXT'\"",
            timeout=8,
        ),
    )
    # endregion

    # region agent log
    log_event(
        "J",
        "scripts/diagnostics/debug_connection.py:163",
        "nginx to web via container IP",
        run_cmd(
            "WEB_IP=$(sudo docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' fightsftickets-web-1) && "
            "cd /home/evan/Documents/Projects/FightSFTickets && "
            "sudo docker compose exec -T nginx sh -lc \"wget -qO- --timeout=5 http://$WEB_IP:3000 2>&1 | head -5\"",
            timeout=8,
        ),
    )
    # endregion

    # region agent log
    log_event(
        "G",
        "scripts/diagnostics/debug_connection.py:117",
        "nginx error log tail",
        run_cmd(
            "cd /home/evan/Documents/Projects/FightSFTickets && "
            "sudo docker compose logs nginx --tail 20"
        ),
    )
    # endregion

    # region agent log
    log_event(
        "C",
        "scripts/diagnostics/debug_connection.py:128",
        "nginx logs",
        run_cmd(
            "cd /home/evan/Documents/Projects/FightSFTickets && sudo docker compose logs nginx --tail 10"
        ),
    )
    # endregion

    # region agent log
    log_event(
        "D",
        "scripts/diagnostics/debug_connection.py:139",
        "ufw status",
        run_cmd("sudo ufw status"),
    )
    # endregion


if __name__ == "__main__":
    main()
