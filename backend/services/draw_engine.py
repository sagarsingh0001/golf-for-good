"""Draw engine and prize calculations."""
import random
from collections import Counter
from typing import List

# Subscription prices (USD)
MONTHLY_PRICE = 9.99
YEARLY_PRICE = 99.0  # discounted (2 months free)

# Share of subscription directed to prize pool (after charity min 10%)
PRIZE_POOL_SHARE = 0.50  # 50% of subscription goes to prize pool

PRIZE_SPLIT = {"tier_5": 0.40, "tier_4": 0.35, "tier_3": 0.25}


def random_numbers(count: int = 5, lo: int = 1, hi: int = 45) -> List[int]:
    return sorted(random.sample(range(lo, hi + 1), count))


def algorithmic_numbers(all_scores: List[int], count: int = 5, lo: int = 1, hi: int = 45) -> List[int]:
    """Weighted by most frequent scores across all users (top half)."""
    if not all_scores:
        return random_numbers(count, lo, hi)
    freq = Counter([s for s in all_scores if lo <= s <= hi])
    # Use top 20 most frequent as pool, then random-sample 5
    most = [n for n, _ in freq.most_common(20)]
    pool = list(set(most))
    if len(pool) < count:
        extra = [n for n in range(lo, hi + 1) if n not in pool]
        random.shuffle(extra)
        pool.extend(extra[: count - len(pool)])
    return sorted(random.sample(pool, count))


def count_matches(user_nums: List[int], winning: List[int]) -> int:
    return len(set(user_nums) & set(winning))


def compute_prize_pool(active_subscriptions_total: float, rolled_over: float = 0.0) -> dict:
    """Returns pool amounts per tier."""
    pool = active_subscriptions_total * PRIZE_POOL_SHARE
    return {
        "total_pool": round(pool, 2),
        "tier_5": round(pool * PRIZE_SPLIT["tier_5"] + rolled_over, 2),
        "tier_4": round(pool * PRIZE_SPLIT["tier_4"], 2),
        "tier_3": round(pool * PRIZE_SPLIT["tier_3"], 2),
    }
