import docker
import json
import logging
import tarfile
import io
import time
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ExecutionService:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            logger.error(f"Failed to connect to Docker daemon: {e}")
            self.client = None

    def _create_tar_stream(self, content: str, filename: str) -> io.BytesIO:
        """Create a tar stream containing a single file."""
        tar_stream = io.BytesIO()
        data = content.encode('utf-8')
        
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            tarinfo = tarfile.TarInfo(name=filename)
            tarinfo.size = len(data)
            tarinfo.mtime = time.time()
            tar.addfile(tarinfo, io.BytesIO(data))
            
        tar_stream.seek(0)
        return tar_stream

    async def execute_code(self, code: str, language: str, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.client:
            return [{"error": "Execution service unavailable"}]

        image_name = f"meetcode-{language}"
        
        # Prepare payload
        payload = {
            "code": code,
            "test_cases": test_cases
        }
        payload_json = json.dumps(payload)
        
        container = None
        try:
            # Start container in detached mode, doing nothing but waiting
            container = self.client.containers.run(
                image=image_name,
                command="tail -f /dev/null",  # Keep alive
                detach=True,
                mem_limit="128m",
                cpu_period=100000,
                cpu_quota=50000, # 50% CPU
                network_disabled=True,
                user="coderunner"
            )
            
            # Inject payload
            tar_stream = self._create_tar_stream(payload_json, "payload.json")
            container.put_archive("/app", tar_stream)
            
            # Execute runner
            # We use sh -c to allow redirection. 
            # In compiled images (Java/C++), we use python3. In python image, we use python.
            python_cmd = "python3" if language in ["java", "cpp"] else "python"
            
            exit_code, output = container.exec_run(
                cmd=["sh", "-c", f"{python_cmd} runner.py < payload.json"],
                user="coderunner",
                workdir="/app"
            )
            
            if exit_code != 0:
                logger.error(f"Runner failed with code {exit_code}: {output.decode('utf-8')}")
                return [{"error": "Runtime Error", "details": output.decode('utf-8')}]

            # Parse results
            result_json = output.decode('utf-8').strip()
            # Sometimes there might be extra noise in stdout if not careful, but our runner is careful
            try:
                results = json.loads(result_json)
                return results
            except json.JSONDecodeError:
                 return [{"error": "System Error", "details": "Invalid output from runner", "raw_output": result_json}]

        except Exception as e:
            logger.error(f"Docker execution error: {e}")
            return [{"error": f"Execution failed: {str(e)}"}]
        
        finally:
            if container:
                try:
                    container.kill()
                    container.remove()
                except Exception as e:
                    logger.error(f"Failed to cleanup container: {e}")
