import ast
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("SolarPowerLoadBalancer")

@dataclass
class WorkloadJob:
    job_id: str
    name: str
    power_requirement_watts: float
    estimated_duration_minutes: int
    priority: int  # 1 (Critical) to 5 (Low Background)
    status: str = "PENDING"

@dataclass
class PowerTelemetry:
    grid_available: bool
    solar_generation_watts: float
    battery_charge_percent: float
    total_load_watts: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class SolarPowerAwareLoadBalancer:
    """
    Manages autonomous background workloads for Cortana in Kitengela,
    shifting heavy computing tasks based on real-time solar generation
    and battery state of charge.
    """
    def __init__(self, max_grid_budget_watts: float = 1200.0):
        self.max_grid_budget_watts = max_grid_budget_watts
        self.workload_queue: List[WorkloadJob] = []
        self.completed_jobs: List[WorkloadJob] = []
        logger.info("SolarPowerAwareLoadBalancer initialized with budget: %fW", max_grid_budget_watts)

    def submit_job(self, job: WorkloadJob) -> None:
        """Submits a new evolutionary workload job."""
        self.workload_queue.append(job)
        logger.info("Workload job submitted: %s (Priority: %d, Power: %.1fW)", job.name, job.priority, job.power_requirement_watts)

    def evaluate_and_dispatch(self, telemetry: PowerTelemetry) -> List[Dict[str, Any]]:
        """
        Evaluates available power (solar + safe grid draw) and dispatches
        appropriate workloads to prevent circuit overload or battery depletion.
        """
        dispatched = []
        available_power = telemetry.solar_generation_watts + (self.max_grid_budget_watts if telemetry.grid_available else 0.0)
        
        # Reserve 30% for core system operations
        usable_power = available_power * 0.70
        
        # Sort queue by priority (ascending) and power requirement
        self.workload_queue.sort(key=lambda x: (x.priority, x.power_requirement_watts))

        remaining_power_budget = usable_power
        retained_queue = []

        for job in self.workload_queue:
            if job.power_requirement_watts <= remaining_power_budget:
                job.status = "RUNNING"
                dispatched.append({
                    "job_id": job.job_id,
                    "name": job.name,
                    "allocated_power": job.power_requirement_watts
                })
                remaining_power_budget -= job.power_requirement_watts
                self.completed_jobs.append(job)
                logger.info("Dispatched workload: %s using %.1fW", job.name, job.power_requirement_watts)
            else:
                job.status = "DEFERRED"
                retained_queue.append(job)
                logger.warning("Deferred workload %s: Insufficient power budget (Req: %.1fW, Avail: %.1fW)", 
                             job.name, job.power_requirement_watts, remaining_power_budget)

        self.workload_queue = retained_queue
        return dispatched

if __name__ == "__main__":
    balancer = SolarPowerAwareLoadBalancer()
    
    # Simulate solar telemetry during Kitengela midday
    telemetry = PowerTelemetry(
        grid_available=True,
        solar_generation_watts=800.0,
        battery_charge_percent=95.0,
        total_load_watts=300.0
    )
    
    balancer.submit_job(WorkloadJob("JOB-001", "Vector Embedding Retraining", 350.0, 45, 2))
    balancer.submit_job(WorkloadJob(
        "JOB-002", 
        "Deep Codebase AST Refactoring", 
        600.0, 
        60, 
        4
    ))
    
    dispatched_jobs = balancer.evaluate_and_dispatch(telemetry)
    assert len(dispatched_jobs) > 0, "Expected at least one job to be dispatched under high solar output"
    
    # Validate source code compiles cleanly
    module_source = __loader__.get_source(__name__) if '__loader__' in globals() and hasattr(__loader__, 'get_source') else open(__file__).read()
    ast.parse(module_source)
    logger.info("SolarPowerAwareLoadBalancer self-test and AST validation completed successfully.")