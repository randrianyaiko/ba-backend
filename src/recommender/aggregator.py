from collections import defaultdict
from typing import List, Dict, Tuple


class InteractionAggregator:
    """
    Aggregates item interaction scores from multiple similar users.
    """

    def __init__(self, mode: str = "sum"):
        """
        Args:
            mode (str): 'sum' or 'average' — defines how to combine similar users' scores.
        """
        self.mode = mode

    def aggregate(
        self,
        similar_users: List[Dict[str, List[float]]],
        exclude_indices: List[int],
        top_k: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Combine sparse vectors from similar users into item recommendations.

        Args:
            similar_users: List of dicts with 'indices' and 'values'
            exclude_indices: Items the target user already interacted with
            top_k: Number of top items to return

        Returns:
            Sorted list of (item_index, aggregated_score)
        """
        score_map = defaultdict(list)

        # Step 1: aggregate contributions
        for user in similar_users:
            for idx, val in zip(user["indices"], user["values"]):
                score_map[idx].append(val)

        # Step 2: compute final score per item
        aggregated_scores = {}
        for idx, vals in score_map.items():
            if idx in exclude_indices:
                continue
            if self.mode == "average":
                aggregated_scores[idx] = sum(vals) / len(vals)
            else:  # default = sum
                aggregated_scores[idx] = sum(vals)

        # Step 3: sort by score descending
        sorted_scores = sorted(aggregated_scores.items(), key=lambda x: x[1], reverse=True)

        return sorted_scores[:top_k]
