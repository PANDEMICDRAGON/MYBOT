import time
import logging
from dataclasses import dataclass
from typing import List, Optional, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WaterSource:
    name: str
    capacity: float  # liters
    current_level: float  # liters
    harvest_rate: float  # liters per hour
    quality_score: float  # 0-1

class DroughtResilienceOptimizer:
    def __init__(self):
        self.sources: List[WaterSource] = []
        self.storage_tanks: List[WaterSource] = []
        self.usage_profile: Dict[str, float] = {}
        self.drought_threshold: float = 0.3  # 30% of capacity

    def add_source(self, source: WaterSource):
        self.sources.append(source)
        logger.info(f"Added water source: {source.name}")

    def add_storage(self, tank: WaterSource):
        self.storage_tanks.append(tank)
        logger.info(f"Added storage tank: {tank.name}")

    def set_usage_profile(self, profile: Dict[str, float]):
        self.usage_profile = profile
        logger.info("Usage profile updated")

    def calculate_total_capacity(self) -> float:
        return sum(tank.capacity for tank in self.storage_tanks)

    def calculate_current_storage(self) -> float:
        return sum(tank.current_level for tank in self.storage_tanks)

    def calculate_harvest_potential(self, hours: float) -> float:
        return sum(source.harvest_rate * hours for source in self.sources)

    def is_drought_condition(self) -> bool:
        total_capacity = self.calculate_total_capacity()
        if total_capacity == 0:
            return False
        current_storage = self.calculate_current_storage()
        return (current_storage / total_capacity) < self.drought_threshold

    def optimize_water_usage(self, hours: float) -> Dict[str, float]:
        if not self.is_drought_condition():
            return self.usage_profile

        total_capacity = self.calculate_total_capacity()
        current_storage = self.calculate_current_storage()
        harvest_potential = self.calculate_harvest_potential(hours)
        available_water = current_storage + harvest_potential

        total_usage = sum(self.usage_profile.values())
        if total_usage == 0:
            return self.usage_profile

        scale_factor = min(1.0, available_water / (total_usage * hours))
        optimized_profile = {key: value * scale_factor for key, value in self.usage_profile.items()}
        logger.info(f"Optimized water usage during drought: {optimized_profile}")
        return optimized_profile

    def run_simulation(self, hours: float = 24) -> Dict[str, float]:
        optimized_usage = self.optimize_water_usage(hours)
        total_usage = sum(optimized_usage.values()) * hours
        current_storage = self.calculate_current_storage()
        harvest_potential = self.calculate_harvest_potential(hours)
        final_storage = max(0, current_storage + harvest_potential - total_usage)

        result = {
            "initial_storage": current_storage,
            "harvest_potential": harvest_potential,
            "total_usage": total_usage,
            "final_storage": final_storage,
            "optimized_profile": optimized_usage,
            "drought_condition": self.is_drought_condition()
        }
        logger.info(f"Simulation result: {result}")
        return result

if __name__ == "__main__":
    optimizer = DroughtResilienceOptimizer()
    
    # Add water sources
    optimizer.add_source(WaterSource("Rainwater Harvesting", 1000, 0, 50, 0.9))
    optimizer.add_source(WaterSource("Groundwater Well", 500, 0, 20, 0.8))
    
    # Add storage tanks
    optimizer.add_storage(WaterSource("Main Tank", 2000, 500, 0, 1.0))
    optimizer.add_storage(WaterSource("Backup Tank", 1000, 200, 0, 1.0))
    
    # Set usage profile
    optimizer.set_usage_profile({
        "drinking": 100,
        "cooking": 50,
        "cleaning": 150,
        "gardening": 100
    })
    
    # Run simulation
    result = optimizer.run_simulation(hours=24)
    print("Drought Resilience Simulation Result:")
    for key, value in result.items():
        print(f"  {key}: {value}")
