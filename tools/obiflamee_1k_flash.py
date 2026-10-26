"""OBIFLAMEE 1K Flash Forwarder -> obiflamee_revenue.py"""
import json
from tools.obiflamee_revenue import generate_flash_strategies

if __name__ == "__main__":
    print(json.dumps(generate_flash_strategies(), indent=2))
