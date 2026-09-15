import httpx
import time
import base64
import subprocess
import tempfile
import os
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.core.logging import log_event

# Standard Judge0 CE language IDs
LANGUAGE_MAP: Dict[str, int] = {
    "c": 75,       # C (GCC 11.1.0) / fallback 50
    "cpp": 105,    # C++ (GCC 14.1.0) / fallback 54
    "java": 62,    # Java (OpenJDK 13.0.1)
    "python": 71,  # Python (3.8.1)
    "py": 71
}

def _evaluate_output(actual_stdout: str, expected_output: Optional[str], exec_time: float) -> Dict[str, Any]:
    stdout_clean = actual_stdout.rstrip('\r\n')
    status = "ACCEPTED"
    if expected_output is not None:
        expected_clean = expected_output.rstrip('\r\n')
        if stdout_clean != expected_clean:
            status = "WRONG_ANSWER"
    return {
        "status": status,
        "stdout": actual_stdout,
        "stderr": "",
        "compile_output": None,
        "time": exec_time,
        "memory": 1024,
        "raw_description": "Accepted" if status == "ACCEPTED" else "Wrong Answer"
    }

async def execute_locally(
    source_code: str,
    language: str,
    stdin_data: str = "",
    expected_output: Optional[str] = None,
    cpu_time_limit: float = 3.0
) -> Dict[str, Any]:
    lang = language.lower().strip()
    stdin_bytes = stdin_data.encode('utf-8') if stdin_data else b""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        start_time = time.time()
        
        try:
            if lang in ["python", "py"]:
                filepath = os.path.join(temp_dir, "solution.py")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(source_code)
                cmd = ["python", filepath]
                proc = subprocess.run(cmd, input=stdin_bytes, capture_output=True, timeout=cpu_time_limit)
                exec_time = round((time.time() - start_time) * 1000, 2)
                
                if proc.returncode != 0:
                    return {
                        "status": "RUNTIME_ERROR",
                        "stdout": proc.stdout.decode('utf-8', errors='replace'),
                        "stderr": proc.stderr.decode('utf-8', errors='replace'),
                        "compile_output": None,
                        "time": exec_time,
                        "memory": None
                    }
                return _evaluate_output(proc.stdout.decode('utf-8', errors='replace'), expected_output, exec_time)

            elif lang in ["c"]:
                src_path = os.path.join(temp_dir, "solution.c")
                exe_path = os.path.join(temp_dir, "solution.exe")
                with open(src_path, "w", encoding="utf-8") as f:
                    f.write(source_code)
                
                comp = subprocess.run(["gcc", src_path, "-o", exe_path], capture_output=True, timeout=10)
                if comp.returncode != 0:
                    return {
                        "status": "COMPILATION_ERROR",
                        "stdout": None,
                        "stderr": None,
                        "compile_output": comp.stderr.decode('utf-8', errors='replace'),
                        "time": 0,
                        "memory": None
                    }
                proc = subprocess.run([exe_path], input=stdin_bytes, capture_output=True, timeout=cpu_time_limit)
                exec_time = round((time.time() - start_time) * 1000, 2)
                if proc.returncode != 0:
                    return {
                        "status": "RUNTIME_ERROR",
                        "stdout": proc.stdout.decode('utf-8', errors='replace'),
                        "stderr": proc.stderr.decode('utf-8', errors='replace'),
                        "compile_output": None,
                        "time": exec_time,
                        "memory": None
                    }
                return _evaluate_output(proc.stdout.decode('utf-8', errors='replace'), expected_output, exec_time)

            elif lang in ["cpp"]:
                src_path = os.path.join(temp_dir, "solution.cpp")
                exe_path = os.path.join(temp_dir, "solution.exe")
                with open(src_path, "w", encoding="utf-8") as f:
                    f.write(source_code)
                
                comp = subprocess.run(["g++", "-std=c++17", src_path, "-o", exe_path], capture_output=True, timeout=10)
                if comp.returncode != 0:
                    return {
                        "status": "COMPILATION_ERROR",
                        "stdout": None,
                        "stderr": None,
                        "compile_output": comp.stderr.decode('utf-8', errors='replace'),
                        "time": 0,
                        "memory": None
                    }
                proc = subprocess.run([exe_path], input=stdin_bytes, capture_output=True, timeout=cpu_time_limit)
                exec_time = round((time.time() - start_time) * 1000, 2)
                if proc.returncode != 0:
                    return {
                        "status": "RUNTIME_ERROR",
                        "stdout": proc.stdout.decode('utf-8', errors='replace'),
                        "stderr": proc.stderr.decode('utf-8', errors='replace'),
                        "compile_output": None,
                        "time": exec_time,
                        "memory": None
                    }
                return _evaluate_output(proc.stdout.decode('utf-8', errors='replace'), expected_output, exec_time)

            elif lang in ["java"]:
                class_name = "Main"
                for line in source_code.splitlines():
                    if "public class " in line:
                        parts = line.split("public class ")[1].split("{")[0].split()
                        if parts:
                            class_name = parts[0]
                            break
                
                src_path = os.path.join(temp_dir, f"{class_name}.java")
                with open(src_path, "w", encoding="utf-8") as f:
                    f.write(source_code)
                
                comp = subprocess.run(["javac", src_path], capture_output=True, timeout=10)
                if comp.returncode != 0:
                    return {
                        "status": "COMPILATION_ERROR",
                        "stdout": None,
                        "stderr": None,
                        "compile_output": comp.stderr.decode('utf-8', errors='replace'),
                        "time": 0,
                        "memory": None
                    }
                proc = subprocess.run(["java", "-cp", temp_dir, class_name], input=stdin_bytes, capture_output=True, timeout=cpu_time_limit)
                exec_time = round((time.time() - start_time) * 1000, 2)
                if proc.returncode != 0:
                    return {
                        "status": "RUNTIME_ERROR",
                        "stdout": proc.stdout.decode('utf-8', errors='replace'),
                        "stderr": proc.stderr.decode('utf-8', errors='replace'),
                        "compile_output": None,
                        "time": exec_time,
                        "memory": None
                    }
                return _evaluate_output(proc.stdout.decode('utf-8', errors='replace'), expected_output, exec_time)

            else:
                return {
                    "status": "RUNTIME_ERROR",
                    "stdout": None,
                    "stderr": f"Unsupported language: {language}",
                    "compile_output": None,
                    "time": 0,
                    "memory": None
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "TIME_LIMIT_EXCEEDED",
                "stdout": None,
                "stderr": "Execution timed out.",
                "compile_output": None,
                "time": cpu_time_limit * 1000,
                "memory": None
            }
        except Exception as ex:
            return {
                "status": "RUNTIME_ERROR",
                "stdout": None,
                "stderr": str(ex),
                "compile_output": None,
                "time": 0,
                "memory": None
            }

class Judge0Service:
    """
    Dedicated Code Execution Engine.
    Primary: Remote Judge0 API (when JUDGE0_API_KEY is present)
    Fallback: Sandboxed Local Execution Engine
    """
    def __init__(self):
        self.base_url = settings.JUDGE0_URL.rstrip('/')
        self.api_key = settings.JUDGE0_API_KEY
        self.host = settings.JUDGE0_HOST

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["X-RapidAPI-Key"] = self.api_key
            headers["X-RapidAPI-Host"] = self.host
        return headers

    async def execute_code(
        self,
        source_code: str,
        language: str,
        stdin_data: str = "",
        expected_output: Optional[str] = None,
        cpu_time_limit: float = 3.0,
        memory_limit_kb: int = 128000
    ) -> Dict[str, Any]:
        """
        Executes code via Judge0 REST API, falling back to local runner if unconfigured.
        """
        if not self.api_key:
            # Fallback to local sandbox runner when no API key is provided
            return await execute_locally(source_code, language, stdin_data, expected_output, cpu_time_limit)

        lang_key = language.lower().strip()
        lang_id = LANGUAGE_MAP.get(lang_key, 71)

        payload = {
            "source_code": source_code,
            "language_id": lang_id,
            "stdin": stdin_data,
            "cpu_time_limit": cpu_time_limit,
            "memory_limit": memory_limit_kb
        }
        if expected_output is not None:
            payload["expected_output"] = expected_output

        endpoint = f"{self.base_url}/submissions?wait=true&fields=stdout,stderr,status,time,memory,compile_output"

        try:
            async with httpx.AsyncClient(timeout=settings.JUDGE0_TIMEOUT) as client:
                response = await client.post(endpoint, json=payload, headers=self._get_headers())

            if response.status_code not in (200, 201):
                log_event("JUDGE0_HTTP_ERROR", f"Status {response.status_code}: {response.text}")
                # Fallback to local execution if Judge0 API returns non-200 (e.g. 401/403/500)
                return await execute_locally(source_code, language, stdin_data, expected_output, cpu_time_limit)

            data = response.json()
            status_info = data.get("status", {})
            status_id = status_info.get("id", 3)
            description = status_info.get("description", "Accepted")

            mapped_status = "ACCEPTED"
            if status_id == 3:
                mapped_status = "ACCEPTED"
            elif status_id == 4:
                mapped_status = "WRONG_ANSWER"
            elif status_id == 5:
                mapped_status = "TIME_LIMIT_EXCEEDED"
            elif status_id == 6:
                mapped_status = "COMPILATION_ERROR"
            elif status_id in [7, 8, 9, 10, 11, 12]:
                mapped_status = "RUNTIME_ERROR"
            else:
                mapped_status = "RUNTIME_ERROR"

            return {
                "status": mapped_status,
                "stdout": data.get("stdout"),
                "stderr": data.get("stderr"),
                "compile_output": data.get("compile_output"),
                "time": float(data.get("time")) * 1000 if data.get("time") else None,
                "memory": float(data.get("memory")) if data.get("memory") else None,
                "raw_description": description
            }

        except Exception as e:
            log_event("JUDGE0_CONNECTION_FAILED", str(e))
            return await execute_locally(source_code, language, stdin_data, expected_output, cpu_time_limit)

judge0_service = Judge0Service()
