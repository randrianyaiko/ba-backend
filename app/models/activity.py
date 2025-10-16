from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Dict, Any

@dataclass
class Activity:
    activity_id: str
    user_id: str
    activity_type: str
    product_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    created_at: str = None
    
    def to_dict(self):
        return {
            'activity_id': self.activity_id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'product_id': self.product_id,
            'details': self.details,
            'created_at': self.created_at
        }