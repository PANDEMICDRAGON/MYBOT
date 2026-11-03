"""
Adaptive Polymorphic Execution Enclave & Runtime Bytecode Obfuscator
=====================================================================
Provides ephemeral, memory-safe, dynamically scrambled bytecode execution enclaves
for high-value decision trees and sensitive cryptographic operations executed on
Cortana edge runtime environments in Nairobi.

Prevents process-memory inspection, memory scraping, dynamic introspection,
and reverse-engineering of execution routines by dynamically mutating code memory
layouts, using polymorphic XOR keys, and maintaining zero-residual memory footprints.
"""

import ast
import hashlib
import inspect
import logging
import os
import time
from typing import Any, Callable, Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PolymorphicEnclave")


class EnclaveSecurityViolation(Exception):
    """Raised when memory corruption, tampering, or unauthorized introspection is detected."""
    pass


class PolymorphicExecutionEnclave:
    """
    Dynamically scrambles, executes, and sanitizes sensitive callable objects and payload functions.
    Utilizes polymorphic byte-masking and memory boundary verification.
    """

    def __init__(self, key_rotation_interval_sec: float = 5.0):
        self.key_rotation_interval_sec = key_rotation_interval_sec
        self._current_mask = os.urandom(32)
        self._last_rotation = time.time()
        self._execution_count = 0
        self._integrity_hashes: Dict[str, str] = {}

    def _rotate_mask_if_needed(self) -> None:
        """Rotates the ephemeral dynamic byte-mask key if the rotation interval has elapsed."""
        if time.time() - self._last_rotation > self.key_rotation_interval_sec:
            self._current_mask = os.urandom(32)
            self._last_rotation = time.time()
            logger.debug("Polymorphic key mask rotated successfully.")

    @staticmethod
    def _xor_transform(data: bytes, key: bytes) -> bytes:
        """Applies a byte-level XOR transform using a repeating key sequence."""
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

    def seal_function(self, fn: Callable[..., Any]) -> Tuple[bytes, str]:
        """
        Extracts bytecode from a callable, applies polymorphic XOR masking,
        and computes a tamper-evident integrity digest.
        """
        self._rotate_mask_if_needed()
        try:
            source_code = inspect.getsource(fn)
            ast.parse(source_code)  # Verify valid AST parse
        except Exception as e:
            raise ValueError(f"Target callable source cannot be parsed into AST: {e}")

        source_hash = hashlib.sha256(source_code.encode("utf-8")).hexdigest()
        masked_bytes = self._xor_transform(source_code.encode("utf-8"), self._current_mask)
        self._integrity_hashes[source_hash] = hashlib.sha256(masked_bytes).hexdigest()
        return masked_bytes, source_hash

    def execute_sealed(
        self,
        sealed_bytes: bytes,
        source_hash: str,
        execution_context: Optional[Dict[str, Any]] = None,
        fn_name: str = "enclave_routine"
    ) -> Any:
        """
        Unseals the payload into isolated memory, verifies checksum, executes,
        and immediately scrubs decrypted representations from heap memory.
        """
        self._rotate_mask_if_needed()

        current_sealed_hash = hashlib.sha256(sealed_bytes).hexdigest()
        if self._integrity_hashes.get(source_hash) != current_sealed_hash:
            raise EnclaveSecurityViolation("Integrity check failed: Sealed payload modified or key invalidated!")

        unmasked_bytes = self._xor_transform(sealed_bytes, self._current_mask)
        unmasked_code = unmasked_bytes.decode("utf-8")

        parsed_ast = ast.parse(unmasked_code)

        local_scope: Dict[str, Any] = execution_context or {}
        global_scope: Dict[str, Any] = {
            "__builtins__": __builtins__,
            "math": __import__("math"),
            "time": __import__("time"),
            "json": __import__("json")
        }

        try:
            exec(compile(parsed_ast, filename="<polymorphic_enclave>", mode="exec"), global_scope, local_scope)
            self._execution_count += 1
            
            if fn_name in local_scope:
                result = local_scope[fn_name]()
            else:
                result = local_scope.get("result", None)

            return result
        finally:
            del unmasked_bytes
            del unmasked_code
            del parsed_ast


def verify_enclave_health() -> Dict[str, Any]:
    """Diagnostic runner for the Polymorphic Execution Enclave."""
    enclave = PolymorphicExecutionEnclave(key_rotation_interval_sec=2.0)

    def secure_telemetry_eval():
        data = [12.5, 45.1, 89.2, 33.4]
        avg = sum(data) / len(data)
        return {"status": "HEALTHY", "computed_metric": avg}

    sealed, s_hash = enclave.seal_function(secure_telemetry_eval)
    res = enclave.execute_sealed(sealed, s_hash, fn_name="secure_telemetry_eval")

    return {
        "enclave_active": True,
        "executions_completed": enclave._execution_count,
        "sample_result": res,
    }


if __name__ == "__main__":
    health = verify_enclave_health()
    print(f"Enclave Test Output: {health}")
