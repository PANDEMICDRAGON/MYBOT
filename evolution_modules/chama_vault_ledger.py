import ast
import hashlib
import hmac
import json
import logging
import os
import re
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

logging.basicConfig(level=logging.INFO, format='[CHAMA-VAULT] %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChamaVaultLedger:
    """
    Autonomous Chama & Merry-Go-Round Ledger optimized for offline-first operation in
    Kitengela and Nairobi. Manages member rosters, automated contribution cycles,
    M-Pesa SMS parsing for automated deposit matching, loan issuing, and secure ledger hashing.
    """
    
    def __init__(self, db_path: str = "chama_vault.db", secret_key: Optional[bytes] = None) -> None:
        self.db_path = db_path
        self.secret_key = secret_key or os.urandom(32)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the SQLite schema with cryptographic integrity tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS members (
                        member_id TEXT PRIMARY KEY,
                        full_name TEXT NOT NULL,
                        phone_number TEXT NOT NULL,
                        joined_date TEXT NOT NULL,
                        status TEXT DEFAULT 'ACTIVE'
                    );
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cycles (
                        cycle_id TEXT PRIMARY KEY,
                        cycle_name TEXT NOT NULL,
                        contribution_amount REAL NOT NULL,
                        frequency TEXT NOT NULL,
                        current_recipient_id TEXT,
                        start_date TEXT NOT NULL,
                        end_date TEXT,
                        status TEXT DEFAULT 'ACTIVE'
                    );
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ledger_entries (
                        entry_id TEXT PRIMARY KEY,
                        cycle_id TEXT NOT NULL,
                        member_id TEXT NOT NULL,
                        amount REAL NOT NULL,
                        transaction_type TEXT NOT NULL,
                        reference_code TEXT UNIQUE,
                        timestamp TEXT NOT NULL,
                        hmac_signature TEXT NOT NULL
                    );
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS loans (
                        loan_id TEXT PRIMARY KEY,
                        member_id TEXT NOT NULL,
                        principal REAL NOT NULL,
                        interest_rate REAL NOT NULL,
                        due_date TEXT NOT NULL,
                        status TEXT DEFAULT 'PENDING'
                    );
                ''')
                conn.commit()
                logger.info("ChamaVault Ledger database initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def register_member(self, member_id: str, full_name: str, phone_number: str) -> bool:
        """Register a new member into the Chama."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO members (member_id, full_name, phone_number, joined_date) VALUES (?, ?, ?, ?)",
                    (member_id, full_name, phone_number, datetime.utcnow().isoformat())
                )
                conn.commit()
                logger.info(f"Member registered/updated: {full_name} ({member_id})")
                return True
        except Exception as e:
            logger.error(f"Error registering member {member_id}: {e}")
            return False

    def create_cycle(self, cycle_id: str, cycle_name: str, contribution_amount: float, frequency: str) -> bool:
        """Initialize a new merry-go-round or table banking cycle."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO cycles (cycle_id, cycle_name, contribution_amount, frequency, start_date) VALUES (?, ?, ?, ?, ?)",
                    (cycle_id, cycle_name, contribution_amount, frequency, datetime.utcnow().isoformat())
                )
                conn.commit()
                logger.info(f"Cycle created: {cycle_name} ({cycle_id})")
                return True
        except Exception as e:
            logger.error(f"Error creating cycle {cycle_id}: {e}")
            return False

    def parse_mpesa_sms(self, sms_text: str) -> Optional[Dict[str, Any]]:
        """Extract M-Pesa transaction details via regex for automated contribution crediting."""
        pattern = r"([A-Z0-9]+)\s+Confirmed\.\s+Ksh([0-9,]+\.\d{2})\s+received\s+from\s+([A-Z\s]+)\s+([0-9]+)\s+on\s+(\d{1,2}/\d{1,2}/\d{2,4})"
        match = re.search(pattern, sms_text)
        if match:
            ref, amount_str, name, phone, date_str = match.groups()
            amount = float(amount_str.replace(',', ''))
            return {
                "reference_code": ref,
                "amount": amount,
                "sender_name": name.strip(),
                "phone_number": phone,
                "timestamp": date_str
            }
        logger.warning("Failed to parse M-Pesa SMS format.")
        return None

    def record_contribution(self, entry_id: str, cycle_id: str, member_id: str, amount: float, ref_code: str) -> bool:
        """Record a verified contribution and generate cryptographic HMAC signature."""
        timestamp = datetime.utcnow().isoformat()
        raw_payload = f"{entry_id}:{cycle_id}:{member_id}:{amount}:{ref_code}:{timestamp}"
        signature = hmac.new(self.secret_key, raw_payload.encode('utf-8'), hashlib.sha256).hexdigest()

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO ledger_entries (entry_id, cycle_id, member_id, amount, transaction_type, reference_code, timestamp, hmac_signature) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (entry_id, cycle_id, member_id, amount, 'CONTRIBUTION', ref_code, timestamp, signature)
                )
                conn.commit()
                logger.info(f"Contribution recorded for member {member_id}: Ksh {amount} [Ref: {ref_code}]")
                return True
        except sqlite3.IntegrityError:
            logger.error(f"Duplicate reference code detected: {ref_code}")
            return False
        except Exception as e:
            logger.error(f"Error recording contribution: {e}")
            return False

    def audit_ledger_integrity(self) -> bool:
        """Recompute and verify HMAC signatures for all ledger entries."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT entry_id, cycle_id, member_id, amount, reference_code, timestamp, hmac_signature FROM ledger_entries")
                rows = cursor.fetchall()
                
                for row in rows:
                    entry_id, cycle_id, member_id, amount, ref_code, timestamp, stored_sig = row
                    raw_payload = f"{entry_id}:{cycle_id}:{member_id}:{amount}:{ref_code}:{timestamp}"
                    expected_sig = hmac.new(self.secret_key, raw_payload.encode('utf-8'), hashlib.sha256).hexdigest()
                    
                    if not hmac.compare_digest(expected_sig, stored_sig):
                        logger.critical(f"Ledger tamper detected! Entry ID: {entry_id}")
                        return False
                        
            logger.info("Ledger integrity verified successfully. 0 corruptions found.")
            return True
        except Exception as e:
            logger.error(f"Error auditing ledger: {e}")
            return False

    def get_member_balance(self, member_id: str) -> float:
        """Calculate total verified contributions for a member."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT SUM(amount) FROM ledger_entries WHERE member_id = ? AND transaction_type = 'CONTRIBUTION'", (member_id,))
                res = cursor.fetchone()
                return res[0] if res and res[0] else 0.0
        except Exception as e:
            logger.error(f"Error calculating balance for {member_id}: {e}")
            return 0.0


if __name__ == "__main__":
    print("=== TESTING CORTANA CHAMA VAULT LEDGER ===")
    vault = ChamaVaultLedger()
    
    # Register Test Members
    vault.register_member("MEM001", "Michael Obiero", "+254712345678")
    vault.register_member("MEM002", "Brenda Achieng", "+254722334455")
    
    # Create Cycle
    vault.create_cycle("CYC2025-Q1", "Kitengela Tech Innovators Merry-Go-Round", 5000.0, "MONTHLY")
    
    # Test M-Pesa SMS parsing
    sample_sms = "QWE1234567 Confirmed. Ksh5,000.00 received from BRENDA ACHIENG 254722334455 on 15/3/25"
    parsed = vault.parse_mpesa_sms(sample_sms)
    print("Parsed SMS:", parsed)
    
    if parsed:
        vault.record_contribution(
            entry_id="ENT-001",
            cycle_id="CYC2025-Q1",
            member_id="MEM002",
            amount=parsed["amount"],
            ref_code=parsed["reference_code"]
        )
        
    # Audit Integrity
    is_valid = vault.audit_ledger_integrity()
    print(f"Ledger Integrity Check Passed: {is_valid}")
    
    # Check Balance
    bal = vault.get_member_balance("MEM002")
    print(f"Brenda's Total Contributions: Ksh {bal}")
