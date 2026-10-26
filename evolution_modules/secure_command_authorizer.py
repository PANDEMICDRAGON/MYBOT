"""
secure_command_authorizer.py

Provides role‑based command authorization using JWT tokens.
"""

import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional

import jwt  # PyJWT

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AuthorizationError(Exception):
    """Raised when a command execution is not authorized."""
    pass


@dataclass
class Policy:
    """Defines allowed commands for a role."""
    role: str
    allowed_commands: List[str]


class PolicyStore:
    """Loads and caches role policies from a JSON file."""

    def __init__(self, policy_path: Path):
        self.policy_path = policy_path
        self._policies: Dict[str, Policy] = {}
        self._load_policies()

    def _load_policies(self) -> None:
        if not self.policy_path.is_file():
            raise FileNotFoundError(f"Policy file not found: {self.policy_path}")
        try:
            raw = json.loads(self.policy_path.read_text(encoding="utf-8"))
            for entry in raw:
                policy = Policy(role=entry["role"], allowed_commands=entry["allowed_commands"])
                self._policies[policy.role] = policy
        except (json.JSONDecodeError, KeyError) as exc:
            raise ValueError(f"Invalid policy format: {exc}") from exc

    def is_allowed(self, role: str, command: str) -> bool:
        policy = self._policies.get(role)
        return policy is not None and command in policy.allowed_commands


class SecureCommandExecutor:
    """Executes functions only after verifying JWT token and policy."""

    def __init__(self, policy_store: PolicyStore, secret: str, algorithms: Optional[List[str]] = None):
        self.policy_store = policy_store
        self.secret = secret
        self.algorithms = algorithms or ["HS256"]

    def _decode_token(self, token: str) -> Dict:
        try:
            payload = jwt.decode(token, self.secret, algorithms=self.algorithms)
            return payload
        except jwt.PyJWTError as exc:
            raise AuthorizationError(f"Token validation failed: {exc}") from exc

    def authorize(self, token: str, command_name: str) -> None:
        payload = self._decode_token(token)
        role = payload.get("role")
        if not role:
            raise AuthorizationError("Token missing 'role' claim")
        if not self.policy_store.is_allowed(role, command_name):
            raise AuthorizationError(f"Role '{role}' not permitted to run '{command_name}'")

    def execute(self, token: str, command: Callable[..., None], *args, **kwargs) -> None:
        command_name = getattr(command, "__name__", str(command))
        self.authorize(token, command_name)
        logger.info(
            "Authorized execution of %s by role %s at %s",
            command_name,
            self._decode_token(token).get("role"),
            datetime.now(timezone.utc).isoformat(),
        )
        try:
            command(*args, **kwargs)
        except Exception as exc:
            logger.exception("Command %s raised an exception", command_name)
            raise


def sample_command(message: str) -> None:
    """A demo command that could be protected."""
    print(f"[SECURE] {message}")


def _generate_demo_token(secret: str, role: str) -> str:
    payload = {"role": role, "iat": datetime.now(tz=timezone.utc)}
    return jwt.encode(payload, secret, algorithm="HS256")


if __name__ == "__main__":
    # Demo setup
    demo_policy_path = Path(__file__).with_name("demo_policy.json")
    demo_policy_path.write_text(
        json.dumps(
            [
                {"role": "admin", "allowed_commands": ["sample_command"]},
                {"role": "operator", "allowed_commands": []},
            ]
        ),
        encoding="utf-8",
    )

    store = PolicyStore(demo_policy_path)
    secret_key = "super-secret-key"
    executor = SecureCommandExecutor(store, secret_key)

    admin_token = _generate_demo_token(secret_key, "admin")
    operator_token = _generate_demo_token(secret_key, "operator")

    # Should succeed
    executor.execute(admin_token, sample_command, "Hello, Michael!")

    # Should fail
    try:
        executor.execute(operator_token, sample_command, "You shall not pass")
    except AuthorizationError as e:
        print(f"Authorization failed as expected: {e}")
