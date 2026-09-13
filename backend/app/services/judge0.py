import httpx
import time
import base64
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

class Judge0Service:
    """
    Dedicated Judge0 HTTP Client.
    MANDATORY RULE: Judge0 is the ONLY code-execution engine.
    NEVER executes participant code locally or via subprocess.
    Returns 'SERVICE_UNAVAILABLE' if Judge0 is unreachable.
    """
    def __init__(self):
        self.base_url = settings.JUDGE0_URL.rstrip('/')
        self.api_key = settings.JUDGE0_API_KEY
        self.host = settings.JUDGE0_HOST

    def _get_headers() -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json"
        }
        if settings.JUDGE0_API_KEY:
            headers["X-RapidAPI-Key"] = settings.JUDGE0_API_KEY
            headers["X-RapidAPI-Host"] = settings.JUDGE0_HOST
        return headers

    async def execute_code(
        self,
        source_code: str,
        language: str,
        stdin_data: str = "",
        expected_output: Optional[str] = None,
        cpu_time_limit: float = 2.0,
        memory_limit_kb: int = 128000
    ) -> Dict[str, Any]:
        """
        Executes code remotely via Judge0 REST API.
        """
        lang_key = language.lower().strip()
        lang_id = LANGUAGE_MAP.get(lang_key, 71) # default python

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
                return {
                    "status": "SERVICE_UNAVAILABLE",
                    "stdout": None,
                    "stderr": None,
                    "compile_output": None,
                    "time": None,
                    "memory": None,
                    "error_message": "Code execution service unavailable. Please try again shortly or notify an administrator."
                }

            data = response.json()
            status_info = data.get("status", {})
            status_id = status_info.get("id", 3)
            description = status_info.get("description", "Accepted")

            # Map Judge0 status IDs
            # 3: Accepted, 4: Wrong Answer, 5: Time Limit Exceeded, 6: Compilation Error, 7-12: Runtime Errors
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
                "time": float(data.get("time")) * 1000 if data.get("time") else None, # ms
                "memory": float(data.get("memory")) if data.get("memory") else None, # kb
                "raw_description": description
            }

        except Exception as e:
            log_event("JUDGE0_CONNECTION_FAILED", str(e))
            return {
                "status": "SERVICE_UNAVAILABLE",
                "stdout": None,
                "stderr": None,
                "compile_output": None,
                "time": None,
                "memory": None,
                "error_message": "Code execution service unavailable. Please try again shortly or notify an administrator."
            }

judge0_service = Judge0Service()
