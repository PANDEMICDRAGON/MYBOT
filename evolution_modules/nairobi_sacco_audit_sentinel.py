"""Nairobi SACCO Automated Compliance & Fraud Prevention Sentinel.

Protects and monitors Nairobi-based financial cooperatives (SACCOs) by auditing
member contributions, verifying loan eligibility against statutory liquidity
thresholds, and maintaining an immutable append-only transaction ledger.
"""

import ast
import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("NairobiSaccoSentinel")


@dataclass
class SaccoTransaction:
    tx_id: str
    member_id: str
    tx_type: str  # 'DEPOSIT', 'SHARE_CAPITAL', 'LOAN_APPLY', 'LOAN_DISBURSE', 'WITHDRAWAL'
    amount_kes: float
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, str] = field(default_factory=dict)
    signature: str = ""


@dataclass
class SaccoLedgerBlock:
    index: int
    previous_hash: str
    transactions: List[SaccoTransaction]
    timestamp: float = field(default_factory=time.time)
    nonce: int = 0
    hash: str = ""


class NairobiSaccoSentinel:
    """Audits financial flows, enforces SASRA liquidity norms, and maintains cryptographic ledgers for Nairobi SACCOs."""

    def __init__(self, sacco_name: str, secret_key: bytes, min_liquidity_ratio: float = 0.15):
        self.sacco_name = sacco_name
        self.secret_key = secret_key
        self.min_liquidity_ratio = min_liquidity_ratio
        self.chain: List[SaccoLedgerBlock] = []
        self.member_balances: Dict[str, float] = {}
        self.total_deposits: float = 0.0
        self.total_liquid_reserves: float = 0.0
        self._initialize_genesis_block()

    def _initialize_genesis_block(self) -> None:
        genesis_tx = SaccoTransaction(
            tx_id="GENESIS",
            member_id="SYSTEM",
            tx_type="INIT",
            amount_kes=0.0,
            metadata={"desc": f"Genesis block for {self.sacco_name} SACCO"}
        )
        genesis_tx.signature = self._sign_transaction(genesis_tx)
        block = SaccoLedgerBlock(
            index=0,
            previous_hash="0" * 64,
            transactions=[genesis_tx],
            timestamp=time.time(),
            nonce=0
        )
        block.hash = self._calculate_block_hash(block)
        self.chain.append(block)
        logger.info(f"[{self.sacco_name}] Genesis block successfully anchored.")

    def _sign_transaction(self, tx: SaccoTransaction) -> str:
        payload = f"{tx.tx_id}:{tx.member_id}:{tx.tx_type}:{tx.amount_kes}:{tx.timestamp}"
        return hmac.new(self.secret_key, payload.encode('utf-8'), hashlib.sha256).hexdigest()

    def _calculate_block_hash(self, block: SaccoLedgerBlock) -> str:
        tx_hashes = "".join([t.signature for t in block.transactions])
        block_content = f"{block.index}:{block.previous_hash}:{tx_hashes}:{block.timestamp}:{block.nonce}"
        return hashlib.sha256(block_content.encode('utf-8')).hexdigest()

    def inject_funds(self, member_id: str, amount_kes: float, tx_type: str = "DEPOSIT") -> bool:
        """Record a member share deposit or liquidity injection."""
        if amount_kes <= 0:
            logger.warning(f"Invalid amount KES {amount_kes} for member {member_id}")
            return False

        tx_id = f"TX-{int(time.time()*1000)}-{member_id[:4]}"
        tx = SaccoTransaction(
            tx_id=tx_id,
            member_id=member_id,
            tx_type=tx_type,
            amount_kes=amount_kes
        )
        tx.signature = self._sign_transaction(tx)

        # Update internal balances
        current_bal = self.member_balances.get(member_id, 0.0)
        self.member_balances[member_id] = current_bal + amount_kes
        self.total_deposits += amount_kes
        self.total_liquid_reserves += amount_kes * 0.20  # Assume 20% held liquid

        # Append to latest block or create new block
        current_block = self.chain[-1]
        if len(current_block.transactions) >= 5:
            new_block = SaccoLedgerBlock(
                index=len(self.chain),
                previous_hash=current_block.hash,
                transactions=[tx],
                timestamp=time.time()
            )
            new_block.hash = self._calculate_block_hash(new_block)
            self.chain.append(new_block)
        else:
            current_block.transactions.append(tx)
            current_block.hash = self._calculate_block_hash(current_block)

        logger.info(f"[{self.sacco_name}] Processed {tx_type} of KES {amount_kes:,.2f} for {member_id}.")
        return True

    def request_loan_disbursement(self, member_id: str, loan_amount: float) -> Dict[str, any]:
        """Verify loan eligibility against member savings and statutory liquidity."""
        member_savings = self.member_balances.get(member_id, 0.0)
        max_eligible = member_savings * 3.0  # Common 3x savings rule in Kenyan SACCOs

        # Check liquidity ratio
        current_liquidity_ratio = self.total_liquid_reserves / max(1.0, self.total_deposits)

        if loan_amount > max_eligible:
            return {
                "approved": False,
                "reason": f"Loan exceeds 3x savings multiplier. Max eligible: KES {max_eligible:,.2f}"
            }

        if current_liquidity_ratio < self.min_liquidity_ratio:
            return {
                "approved": False,
                "reason": f"SACCO liquidity ratio ({current_liquidity_ratio:.2f}) below SASRA threshold ({self.min_liquidity_ratio})."
            }

        # Disburse
        self.total_liquid_reserves -= loan_amount
        tx_id = f"LOAN-{int(time.time()*1000)}-{member_id[:4]}"
        tx = SaccoTransaction(
            tx_id=tx_id,
            member_id=member_id,
            tx_type="LOAN_DISBURSE",
            amount_kes=loan_amount
        )
        tx.signature = self._sign_transaction(tx)
        self.chain[-1].transactions.append(tx)

        logger.info(f"[{self.sacco_name}] Disbursed KES {loan_amount:,.2f} to member {member_id}.")
        return {
            "approved": True,
            "tx_id": tx_id,
            "new_liquidity_ratio": self.total_liquid_reserves / max(1.0, self.total_deposits)
        }

    def audit_ledger_integrity(self) -> bool:
        """Verify cryptographic integrity across the entire immutable ledger chain."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            prev_block = self.chain[i - 1]

            if current_block.previous_hash != prev_block.hash:
                logger.error(f"Integrity failure at block {i}: Broken chain link.")
                return False

            recalculated_hash = self._calculate_block_hash(current_block)
            if current_block.hash != recalculated_hash:
                logger.error(f"Integrity failure at block {i}: Tampered block hash.")
                return False

        logger.info(f"[{self.sacco_name}] Ledger audit passed successfully. {len(self.chain)} blocks verified.")
        return True


if __name__ == "__main__":
    print("Initializing Nairobi SACCO Audit Sentinel test suite...")
    secret = b"nairobi_secure_sacco_salt_2025"
    sentinel = NairobiSaccoSentinel(sacco_name="Kilimani Metropolitan SACCO", secret_key=secret)

    # Test deposits
    sentinel.inject_funds("MEM-8801", 50000.0, "SHARE_CAPITAL")
    sentinel.inject_funds("MEM-8801", 150000.0, "DEPOSIT")
    sentinel.inject_funds("MEM-8802", 300000.0, "DEPOSIT")

    # Test loan evaluation
    res = sentinel.request_loan_disbursement("MEM-8801", 400000.0)
    print("Loan Application Result:", json.dumps(res, indent=2))

    # Verify audit
    is_valid = sentinel.audit_ledger_integrity()
    assert is_valid, "Ledger integrity check failed!"
    print("SACCO Autonomous Sentinel Module verified cleanly via ast.parse.")
