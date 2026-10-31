import ast
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random


class SGRTrain:
    """Represents a Standard Gauge Railway train."""

    def __init__(self, train_id: str, origin: str, destination: str, cargo_weight: float, priority: int = 1):
        self.train_id = train_id
        self.origin = origin
        self.destination = destination
        self.cargo_weight = cargo_weight
        self.priority = priority
        self.status = "SCHEDULED"
        self.scheduled_departure: Optional[datetime] = None
        self.actual_departure: Optional[datetime] = None
        self.actual_arrival: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "train_id": self.train_id,
            "origin": self.origin,
            "destination": self.destination,
            "cargo_weight": self.cargo_weight,
            "priority": self.priority,
            "status": self.status,
            "scheduled_departure": self.scheduled_departure.isoformat() if self.scheduled_departure else None,
            "actual_departure": self.actual_departure.isoformat() if self.actual_departure else None,
            "actual_arrival": self.actual_arrival.isoformat() if self.actual_arrival else None
        }


class NairobiSGRCycloidSentinel:
    """
    An autonomous sentinel that optimizes SGR freight train scheduling using a cycloid-based
    predictive model to minimize congestion and maximize throughput in the Nairobi corridor.
    """

    def __init__(self, base_speed_kmh: float = 120.0, congestion_factor: float = 1.2):
        self.base_speed_kmh = base_speed_kmh
        self.congestion_factor = congestion_factor
        self.trains: List[SGRTrain] = []
        self.schedule_log: List[Dict[str, Any]] = []

    def add_train(self, train: SGRTrain) -> None:
        """Add a train to the scheduling queue."""
        self.trains.append(train)

    def calculate_optimal_departure(self, train: SGRTrain, current_time: datetime) -> datetime:
        """
        Calculate the optimal departure time using a cycloid function that models
        Nairobi's traffic and weather patterns.
        """
        # Simulate a cycloid function for congestion
        hour = current_time.hour
        # Peak hours: 7-9 AM, 5-7 PM
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            congestion_multiplier = self.congestion_factor
        else:
            congestion_multiplier = 1.0

        # Cycloid adjustment: sin(pi * hour / 12) to model daily cycle
        cycloid_adjustment = abs(__import__('math').sin(__import__('math').pi * hour / 12))
        optimal_delay_minutes = int(cycloid_adjustment * 30 * congestion_multiplier)

        return current_time + timedelta(minutes=optimal_delay_minutes)

    def optimize_schedule(self, current_time: datetime) -> List[Dict[str, Any]]:
        """
        Optimize the schedule for all trains in the queue.
        """
        # Sort by priority (higher priority first)
        self.trains.sort(key=lambda t: t.priority, reverse=True)

        optimized_schedule = []
        for train in self.trains:
            optimal_departure = self.calculate_optimal_departure(train, current_time)
            train.scheduled_departure = optimal_departure
            train.status = "OPTIMIZED"

            schedule_entry = {
                "train_id": train.train_id,
                "scheduled_departure": optimal_departure.isoformat(),
                "priority": train.priority,
                "cargo_weight": train.cargo_weight
            }
            optimized_schedule.append(schedule_entry)
            self.schedule_log.append(schedule_entry)

        return optimized_schedule

    def simulate_journey(self, train: SGRTrain, current_time: datetime) -> Dict[str, Any]:
        """
        Simulate the journey of a train and update its status.
        """
        if train.scheduled_departure is None:
            raise ValueError(f"Train {train.train_id} has no scheduled departure.")

        # Simulate journey time based on distance and speed
        distance_km = 100.0  # Assume 100km for simulation
        journey_hours = distance_km / self.base_speed_kmh
        journey_time = timedelta(hours=journey_hours)

        train.actual_departure = train.scheduled_departure
        train.actual_arrival = train.scheduled_departure + journey_time
        train.status = "COMPLETED"

        return {
            "train_id": train.train_id,
            "departure": train.actual_departure.isoformat(),
            "arrival": train.actual_arrival.isoformat(),
            "status": train.status
        }

    def get_schedule_summary(self) -> Dict[str, Any]:
        """Get a summary of the current schedule."""
        return {
            "total_trains": len(self.trains),
            "optimized_trains": len([t for t in self.trains if t.status == "OPTIMIZED"]),
            "completed_trains": len([t for t in self.trains if t.status == "COMPLETED"]),
            "schedule_log": self.schedule_log
        }


def main():
    """Test harness for the Nairobi SGR Rail Cycloid Sentinel."""
    try:
        sentinel = NairobiSGRCycloidSentinel()
        current_time = datetime.now()

        # Add sample trains
        train1 = SGRTrain("SGR-001", "Nairobi", "Mombasa", 50.0, priority=2)
        train2 = SGRTrain("SGR-002", "Nairobi", "Mombasa", 30.0, priority=1)
        train3 = SGRTrain("SGR-003", "Nairobi", "Mombasa", 70.0, priority=3)

        sentinel.add_train(train1)
        sentinel.add_train(train2)
        sentinel.add_train(train3)

        # Optimize schedule
        optimized_schedule = sentinel.optimize_schedule(current_time)
        print("Optimized Schedule:")
        print(json.dumps(optimized_schedule, indent=2))

        # Simulate journey for the highest priority train
        journey_result = sentinel.simulate_journey(train3, current_time)
        print("Journey Simulation:")
        print(json.dumps(journey_result, indent=2))

        # Get summary
        summary = sentinel.get_schedule_summary()
        print("Schedule Summary:")
        print(json.dumps(summary, indent=2))

        print("\nTest passed successfully.")
    except Exception as e:
        print(f"Test failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
