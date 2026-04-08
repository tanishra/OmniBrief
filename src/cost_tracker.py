"""
src/cost_tracker.py
Tracks token usage and estimated cost for OpenAI calls.
Prices for GPT-4o and GPT-4o-mini (as of 2024/2025).
"""

import json

# Prices per 1M tokens (USD)
PRICES = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o":      {"input": 2.50, "output": 10.00}
}

class CostTracker:
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.usage_details = [] # List of (model, input, output)

    def log_usage(self, model: str, input_tokens: int, output_tokens: int):
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.usage_details.append({
            "model": model,
            "input": input_tokens,
            "output": output_tokens
        })

    def calculate_total_cost(self) -> float:
        total_cost = 0.0
        for detail in self.usage_details:
            model = detail["model"]
            # Fallback to mini if unknown
            price = PRICES.get(model, PRICES["gpt-4o-mini"])
            cost = (detail["input"] / 1_000_000 * price["input"]) + 
                   (detail["output"] / 1_000_000 * price["output"])
            total_cost += cost
        return total_cost

    def get_summary(self) -> str:
        cost = self.calculate_total_cost()
        return (
            f"
--- 💰 PRIVATE COST AUDIT ---"
            f"
Total Input Tokens:  {self.total_input_tokens:,}"
            f"
Total Output Tokens: {self.total_output_tokens:,}"
            f"
Estimated Run Cost:  ${cost:.4f} (~₹{cost*83:.2f})"
            f"
---------------------------
"
        )

# Global instance for the run
tracker = CostTracker()
