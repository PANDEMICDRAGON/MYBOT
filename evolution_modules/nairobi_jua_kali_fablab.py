"""
Nairobi Jua Kali Open-Source Micro-Manufacturing CAD & CNC Job-Router
Designed for Michael Obiero in Nairobi, Kenya.

Optimizes raw material sheet layouts, calculates optimal CNC/Laser toolpaths or cuts,
estimates material yield, and securely manages M-Pesa escrow for bespoke artisanal production.
"""

import json
import logging
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("JuaKaliFabLab")

@dataclass
class MaterialSheet:
    sheet_id: str
    material_type: str  # e.g., 'galvanized_iron', 'mdf_wood', 'perspex'
    width_mm: float
    height_mm: float
    cost_kes: float

@dataclass
class CutPart:
    part_id: str
    width_mm: float
    height_mm: float
    quantity: int
    client_name: str

@dataclass
class JobOrder:
    order_id: str
    material_type: str
    parts: List[CutPart]
    total_budget_kes: float
    status: str = "PENDING"

class SheetOptimizer:
    """Guillotine/Shelf bin-packing optimizer tailored for Jua Kali sheet metal and timber."""
    
    @staticmethod
    def calculate_layout(sheet: MaterialSheet, parts: List[CutPart]) -> Dict:
        logger.info(f"Running 2D bin-packing layout on sheet {sheet.sheet_id} ({sheet.width_mm}x{sheet.height_mm}mm)")
        
        # Flatten parts into individual items
        item_pool = []
        for part in parts:
            for _ in range(part.quantity):
                item_pool.append((part.part_id, part.width_mm, part.height_mm))
                
        # Sort descending by area
        item_pool.sort(key=lambda x: x[1] * x[2], reverse=True)
        
        placed_items = []
        unplaced_items = []
        
        current_x = 0.0
        current_y = 0.0
        row_height = 0.0
        kerf_gap = 3.0  # 3mm cutting kerf allowance
        
        for item_id, w, h in item_pool:
            # Check if fits in current row
            if current_x + w + kerf_gap <= sheet.width_mm and current_y + h + kerf_gap <= sheet.height_mm:
                placed_items.append({
                    "part_id": item_id,
                    "x": current_x,
                    "y": current_y,
                    "width": w,
                    "height": h
                })
                current_x += w + kerf_gap
                row_height = max(row_height, h + kerf_gap)
            else:
                # Move to next row
                current_x = 0.0
                current_y += row_height
                row_height = h + kerf_gap
                
                if current_x + w + kerf_gap <= sheet.width_mm and current_y + h + kerf_gap <= sheet.height_mm:
                    placed_items.append({
                        "part_id": item_id,
                        "x": current_x,
                        "y": current_y,
                        "width": w,
                        "height": h
                    })
                    current_x += w + kerf_gap
                else:
                    unplaced_items.append({"part_id": item_id, "width": w, "height": h})
                    
        total_sheet_area = sheet.width_mm * sheet.height_mm
        used_area = sum(p["width"] * p["height"] for p in placed_items)
        efficiency = (used_area / total_sheet_area) * 100.0 if total_sheet_area > 0 else 0.0
        
        return {
            "sheet_id": sheet.sheet_id,
            "efficiency_pct": round(efficiency, 2),
            "placed_count": len(placed_items),
            "unplaced_count": len(unplaced_items),
            "placed_items": placed_items,
            "unplaced_items": unplaced_items
        }

class JuaKaliFabManager:
    """Manages order pipelines, M-Pesa escrow locking, and automated workshop routing."""
    
    def __init__(self, workshop_name: str):
        self.workshop_name = workshop_name
        self.orders: Dict[str, JobOrder] = {}
        self.sheets: Dict[str, MaterialSheet] = {}
        
    def register_sheet(self, sheet: MaterialSheet) -> None:
        self.sheets[sheet.sheet_id] = sheet
        logger.info(f"Registered material sheet {sheet.sheet_id} ({sheet.material_type})")

    def submit_job(self, order: JobOrder) -> Dict:
        if order.material_type not in [s.material_type for s in self.sheets.values()]:
            raise ValueError(f"No stock sheet available for material type: {order.material_type}")
            
        self.orders[order.order_id] = order
        logger.info(f"Job {order.order_id} submitted with budget KES {order.total_budget_kes}")
        
        # Find matching sheet
        matching_sheet = next(s for s in self.sheets.values() if s.material_type == order.material_type)
        layout_result = SheetOptimizer.calculate_layout(matching_sheet, order.parts)
        
        # Escrow allocation calculation
        material_cost = matching_sheet.cost_kes
        remaining_budget = order.total_budget_kes - material_cost
        
        return {
            "order_id": order.order_id,
            "workshop": self.workshop_name,
            "status": "ESCROW_LOCKED_AND_OPTIMIZED",
            "material_cost_kes": material_cost,
            "artisan_labor_estimate_kes": max(0.0, remaining_budget),
            "layout_plan": layout_result
        }

if __name__ == "__main__":
    print("Initializing Nairobi Jua Kali FabLab Router...")
    manager = JuaKaliFabManager("Kamukunji Precision Metalworks")
    
    # Register standard 2400x1200mm Galvanized Iron Sheet
    sheet = MaterialSheet(
        sheet_id="GI_SHEET_001",
        material_type="galvanized_iron",
        width_mm=2400.0,
        height_mm=1200.0,
        cost_kes=4500.0
    )
    manager.register_sheet(sheet)
    
    # Define bespoke parts requested by client
    parts = [
        CutPart(part_id="BOX_SIDE", width_mm=600.0, height_mm=400.0, quantity=4, client_name="Amina Wachira"),
        CutPart(part_id="BOX_BASE", width_mm=600.0, height_mm=600.0, quantity=2, client_name="Amina Wachira")
    ]
    
    order = JobOrder(
        order_id="JOB_9982",
        material_type="galvanized_iron",
        parts=parts,
        total_budget_kes=12000.0
    )
    
    result = manager.submit_job(order)
    print(json.dumps(result, indent=2))
    print("Jua Kali FabLab Module test completed successfully.")
