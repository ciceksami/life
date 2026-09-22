"""Avatar Life #2017 economy settings.

Quest/reward systems should import these values instead of hardcoding rewards.
"""

PUBLIC_FREE_GOLD = False
STAFF_TEST_MIN_ROLE = 5

GOLD_TO_SILVER_RATE = 100

# Prepared reward economy for the next quest-system package.
STARTER_QUEST_REWARDS = {
    "create_avatar": {"slvr": 1000},
    "first_purchase": {"gld": 1, "slvr": 500},
    "first_social_action": {"gld": 1},
}

DAILY_QUEST_REWARDS = {
    "login": {"slvr": 500},
    "play_time": {"gld": 2},
    "social": {"gld": 2, "slvr": 500},
    "shopping": {"gld": 2},
}

WEEKLY_QUEST_REWARDS = {
    "active_player": {"gld": 5, "slvr": 2500},
    "social_player": {"gld": 5},
    "shopper": {"gld": 5, "slvr": 2500},
    "weekly_complete": {"gld": 10},
}

# Safety ceilings for automated rewards.
MAX_SINGLE_GOLD_REWARD = 50
MAX_SINGLE_SILVER_REWARD = 100000
MAX_SINGLE_ENERGY_REWARD = 100
