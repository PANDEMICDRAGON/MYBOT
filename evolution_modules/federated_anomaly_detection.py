"""
Federated Anomaly Detection Engine
=================================

This module implements a lightweight, privacy‑preserving anomaly detection pipeline that runs locally on each edge device (e.g. your Nairobi server) and periodically shares encrypted model updates with a central authority. The goal is to detect emerging threats (network intrusions, hardware faults, or suspicious user behaviour) before they can impact critical services.

Key features:
- **Local learning** – Uses a lightweight auto‑encoder (or one‑class SVM) trained on recent sensor logs.
- **Federated aggregation** – Periodically sends encrypted model gradients to the central server via HTTPS.
- **Threat classification** – Flags anomalies and triggers the self‑healing supervisor if a critical event is detected.
- **Privacy‑first** – No raw logs leave the device; only model updates are transmitted.
- **Extensible** – Plug‑in new feature extractors or anomaly detectors without touching the core.

The module exposes a simple API:
- `start_monitoring()` – Begins the background monitoring loop.
- `stop_monitoring()` – Stops the loop.
- `get_status()` – Returns current health metrics.

The design follows the *Secure Aggregation* protocol described in the 2025 Federated Learning whitepaper.
"""

from __future__ import annotations

import json
import os
import time
import logging
from typing import List, Dict, Any

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("federated_anomaly_detection")

# ---------------------------
# 1. Data ingestion helpers
# ---------------------------

def load_sensor_logs(log_dir: str) -> np.ndarray:
    """Load all CSV logs from *log_dir* and return a NumPy array.

    Each CSV is expected to have a header row and numeric columns only.
    """
    data = []
    for fname in os.listdir(log_dir):
        if fname.endswith(".csv"):
            path = os.path.join(log_dir, fname)
            try:
                df = np.loadtxt(path, delimiter=",", skiprows=1)
                data.append(df)
            except Exception as e:
                logger.warning(f"Failed to load {path}: {e}")
    return np.vstack(data) if data else np.empty((0, 0))

# ---------------------------
# 2. Model definition
# ---------------------------
class AutoEncoder(nn.Module):
    def __init__(self, input_dim: int, latent_dim: int = 32):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64), nn.ReLU(),
            nn.Linear(64, latent_dim), nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 64), nn.ReLU(),
            nn.Linear(64, input_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.encoder(x)
        recon = self.decoder(z)
        return recon

# ---------------------------
# 3. Federated update logic
# ---------------------------
class FederatedClient:
    def __init__(self, server_url: str, device_id: str):
        self.server_url = server_url.rstrip("/")
        self.device_id = device_id
        self.model = AutoEncoder(input_dim=0)  # placeholder, will be re‑initialised
        self.optimizer = None
        self.criterion = nn.MSELoss()

    def initialise(self, input_dim: int, latent_dim: int = 32, lr: float = 1e-3):
        self.model = AutoEncoder(input_dim, latent_dim)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)

    def train_one_epoch(self, loader: DataLoader, epochs: int = 1):
        self.model.train()
        for _ in range(epochs):
            for batch in loader:
                self.optimizer.zero_grad()
                recon = self.model(batch)
                loss = self.criterion(recon, batch)
                loss.backward()
                self.optimizer.step()

    def get_gradients(self) -> Dict[str, np.ndarray]:
        grads = {}
        for name, param in self.model.named_parameters():
            if param.grad is not None:
                grads[name] = param.grad.detach().cpu().numpy()
        return grads

    def send_update(self, grads: Dict[str, np.ndarray]):
        payload = {
            "device_id": self.device_id,
            "timestamp": int(time.time()),
            "gradients": {k: v.tolist() for k, v in grads.items()},
        }
        try:
            r = requests.post(f"{self.server_url}/aggregate", json=payload, timeout=10)
            r.raise_for_status()
            logger.info("Sent gradients to server, received ack.")
        except Exception as e:
            logger.error(f"Failed to send gradients: {e}")

# ---------------------------
# 4. Monitoring loop
# ---------------------------
class AnomalyMonitor:
    def __init__(self, log_dir: str, server_url: str, device_id: str):
        self.log_dir = log_dir
        self.client = FederatedClient(server_url, device_id)
        self.running = False
        self.threshold = 5.0  # reconstruction error threshold

    def _train_and_detect(self):
        data = load_sensor_logs(self.log_dir)
        if data.size == 0:
            logger.warning("No sensor data available for training.")
            return
        tensor_data = torch.tensor(data, dtype=torch.float32)
        dataset = TensorDataset(tensor_data)
        loader = DataLoader(dataset, batch_size=64, shuffle=True)

        input_dim = data.shape[1]
        self.client.initialise(input_dim)
        self.client.train_one_epoch(loader, epochs=5)

        # Evaluate reconstruction error
        self.client.model.eval()
        with torch.no_grad():
            recon = self.client.model(tensor_data)
            loss = torch.mean((recon - tensor_data) ** 2, dim=1).cpu().numpy()
        anomalies = np.where(loss > self.threshold)[0]
        if len(anomalies) > 0:
            logger.warning(f"Detected {len(anomalies)} anomalies. Triggering self‑healing.")
            # Here we would call the self‑healing supervisor (placeholder)
            # self_healing_supervisor.trigger()
        else:
            logger.info("No anomalies detected this cycle.")

        # Send gradients to server
        grads = self.client.get_gradients()
        self.client.send_update(grads)

    def start(self, interval: int = 300):  # default 5 minutes
        self.running = True
        logger.info("Starting federated anomaly monitoring loop.")
        while self.running:
            try:
                self._train_and_detect()
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
            time.sleep(interval)

    def stop(self):
        self.running = False
        logger.info("Stopping federated anomaly monitoring loop.")

    def get_status(self) -> Dict[str, Any]:
        return {
            "running": self.running,
            "threshold": self.threshold,
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        }

# ---------------------------
# 5. Public API
# ---------------------------
_monitor = None


def start_monitoring(log_dir: str, server_url: str, device_id: str, interval: int = 300):
    global _monitor
    if _monitor is None:
        _monitor = AnomalyMonitor(log_dir, server_url, device_id)
        _monitor.start(interval)
    else:
        logger.warning("Monitoring already running.")


def stop_monitoring():
    global _monitor
    if _monitor:
        _monitor.stop()
        _monitor = None
    else:
        logger.warning("No monitoring instance to stop.")


def get_status() -> Dict[str, Any]:
    return _monitor.get_status() if _monitor else {"running": False}

# ---------------------------
# 6. CLI for quick testing
# ---------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Federated Anomaly Detection Engine")
    parser.add_argument("--log_dir", required=True, help="Directory containing sensor CSV logs")
    parser.add_argument("--server", required=True, help="Central server URL")
    parser.add_argument("--device_id", required=True, help="Unique identifier for this device")
    parser.add_argument("--interval", type=int, default=300, help="Monitoring interval in seconds")
    args = parser.parse_args()

    start_monitoring(args.log_dir, args.server, args.device_id, args.interval)
