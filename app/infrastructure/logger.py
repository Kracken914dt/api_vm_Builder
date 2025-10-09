import logging
import json
import os
from datetime import datetime
from enum import Enum

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "audit.log")

logger = logging.getLogger("audit")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(LOG_FILE)
    fmt = logging.Formatter("%(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)


def audit_log(actor: str, action: str, vm_id: str, provider, success: bool, details=None):
    # Normalizar provider a string
    if isinstance(provider, Enum):
        provider_value = provider.value
    else:
        provider_value = str(provider)
    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "actor": actor,
        "action": action,
        "vm_id": vm_id,
        "provider": provider_value,
        "success": success,
        "details": details,
    }
    # evitar credenciales sensibles: nunca registramos 'params' completos ni secretos
    logger.info(json.dumps(payload, default=str))
