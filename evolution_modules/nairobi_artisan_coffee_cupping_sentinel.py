import logging
import time
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [ArtisanCoffeeCuppingSentinel]: %(message)s')
logger = logging.getLogger('ArtisanCoffeeCuppingSentinel')

class CoffeeCuppingEngine:
    """
    Evaluates specialty coffee cupping metrics adhering to Coffee Quality Institute (CQI)
    protocols, correlating moisture, density, and sensory notes for Nairobi roasteries.
    """
    def __init__(self, batch_id: str, origin_estate: str):
        self.batch_id = batch_id
        self.origin_estate = origin_estate
        self.scores: List[Dict[str, float]] = []
        self.certified = False
        logger.info(f"Initialized CoffeeCuppingEngine for batch {batch_id} from {origin_estate}.")

    def add_cupping_scorecard(self, cupper_id: str, attributes: Dict[str, float]) -> None:
        """
        Add individual cupper sensory attributes (Fragrance, Flavor, Aftertaste, Acidity, Body, Balance, Clean Cup, Sweetness, Uniformity, Overall).
        Values expected on a scale of 6.0 to 10.0.
        """
        required_attrs = [
            'fragrance_aroma', 'flavor', 'aftertaste', 'acidity',
            'body', 'balance', 'clean_cup', 'sweetness', 'uniformity', 'overall'
        ]
        for attr in required_attrs:
            if attr not in attributes:
                raise ValueError(f"Missing required cupping attribute: {attr}")
            if not (0.0 <= attributes[attr] <= 10.0):
                raise ValueError(f"Attribute {attr} must be between 0.0 and 10.0, got {attributes[attr]}")

        total_score = sum(attributes.values())
        record = {
            'cupper_id': cupper_id,
            'attributes': attributes,
            'total_score': total_score,
            'timestamp': time.time()
        }
        self.scores.append(record)
        logger.info(f"Added scorecard from cupper {cupper_id}. Total Score: {total_score:.2f}/100")

    def compute_final_aggregate(self) -> Dict[str, Any]:
        """
        Computes mean aggregate scores and determines specialty certification status (>80.0).
        """
        if not self.scores:
            return {'batch_id': self.batch_id, 'status': 'PENDING', 'final_score': 0.0}

        avg_total = sum(s['total_score'] for s in self.scores) / len(self.scores)
        self.certified = avg_total >= 80.0

        avg_attributes = {}
        keys = self.scores[0]['attributes'].keys()
        for k in keys:
            avg_attributes[k] = sum(s['attributes'][k] for s in self.scores) / len(self.scores)

        return {
            'batch_id': self.batch_id,
            'origin_estate': self.origin_estate,
            'total_cuppers': len(self.scores),
            'mean_final_score': round(avg_total, 2),
            'attribute_breakdowns': avg_attributes,
            'specialty_certified': self.certified,
            'grade': 'Specialty Grade' if self.certified else 'Commercial Grade'
        }

if __name__ == '__main__':
    print("Executing Nairobi Artisan Coffee Cupping Sentinel self-test...")
    engine = CoffeeCuppingEngine(batch_id="NCH-2023-998", origin_estate="Kiambu Highland Estate")
    
    engine.add_cupping_scorecard('Cupper_Alice', {
        'fragrance_aroma': 8.5, 'flavor': 8.75, 'aftertaste': 8.25, 'acidity': 9.0,
        'body': 8.5, 'balance': 8.5, 'clean_cup': 10.0, 'sweetness': 10.0,
        'uniformity': 10.0, 'overall': 8.75
    })
    
    engine.add_cupping_scorecard('Cupper_Bob', {
        'fragrance_aroma': 8.25, 'flavor': 8.5, 'aftertaste': 8.0, 'acidity': 8.75,
        'body': 8.25, 'balance': 8.25, 'clean_cup': 10.0, 'sweetness': 10.0,
        'uniformity': 10.0, 'overall': 8.5
    })
    
    result = engine.compute_final_aggregate()
    print(f"Cupping Summary Result: {result}")
    print("Sentinel verification complete.")
