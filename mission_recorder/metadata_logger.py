import platform
import subprocess
import datetime
import uuid
import json
import os
import sys

class MetadataLogger:
    """
    Captures comprehensive metadata about the execution environment
    and simulation configuration to ensure reproducibility.
    """
    def __init__(self):
        self.metadata = {}

    def capture(self, config=None):
        """
        Captures all metadata.
        """
        self.capture_system_info()
        self.capture_git_info()
        self.capture_execution_info()
        if config:
            self.metadata['configuration'] = config
        return self.metadata

    def capture_system_info(self):
        """Captures hardware and OS information."""
        self.metadata['system'] = {
            'os': platform.system(),
            'os_release': platform.release(),
            'os_version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'hostname': platform.node()
        }

    def capture_git_info(self):
        """Captures the current git commit hash and status."""
        try:
            # Check if we are in a git repo
            commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL).decode('ascii').strip()
            is_dirty = subprocess.call(['git', 'diff-index', '--quiet', 'HEAD', '--']) != 0
            
            self.metadata['git'] = {
                'commit_hash': commit_hash,
                'is_dirty': is_dirty
            }
        except Exception:
            self.metadata['git'] = {
                'error': "Not a git repository or git not available"
            }

    def capture_execution_info(self):
        """Captures runtime information."""
        self.metadata['execution'] = {
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'uuid': str(uuid.uuid4()),
            'command': sys.argv
        }

    def save(self, filepath):
        """Saves metadata to a JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.metadata, f, indent=4)

if __name__ == "__main__":
    logger = MetadataLogger()
    meta = logger.capture()
    print(json.dumps(meta, indent=4))
