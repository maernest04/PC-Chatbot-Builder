"""LLM client for part recommendations and conversation. Uses OpenAI with env-based API key."""

import logging
from typing import Optional

from openai import OpenAI

from pc_builder.config import Settings

logger = logging.getLogger(__name__)


class ChatSession:
    """Stateful chat session with the assistant for PC building."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or Settings()
        self._client = OpenAI(api_key=self._settings.openai_api_key)
        self._messages: list[dict[str, str]] = [
            {"role": "system", "content": "You are a helpful assistant for building gaming PCs. Be concise and friendly."}
        ]

    def say(self, user_content: str) -> str:
        """Send a user message and return the assistant's reply."""
        self._messages.append({"role": "user", "content": user_content})
        response = self._client.chat.completions.create(
            model=self._settings.openai_model,
            messages=self._messages,
        )
        assistant_content = response.choices[0].message.content or ""
        self._messages.append({"role": "assistant", "content": assistant_content})
        return assistant_content

    def get_part_list_response(self, preferences: str, budget_usd: float) -> str:
        """Ask the model for a comma-separated list of part names (no OS)."""
        prompt = (
            f"User preferences: {preferences}. Budget: ${budget_usd:.0f} USD (excluding OS). "
            "Reply with ONLY a comma-separated list of 8 part names in this exact order: "
            "CPU, CPU Cooler, Motherboard, Memory, Storage, GPU, Case, Power Supply. "
            "Example: Intel i7-13700K, Corsair H100i RGB, MSI MAG B660M Mortar WiFi, "
            "Corsair Vengeance 32GB DDR5-6000, Crucial P3 Plus 2TB NVMe, NVIDIA RTX 4070, "
            "Fractal Design Meshify C, Corsair RM750x 750W. No other text."
        )
        return self.say(prompt).strip()

    def get_tax_rate_response(self, state_or_region: str) -> str:
        """Ask for a numeric tax rate (e.g. 0.0725) for the given state/region."""
        prompt = (
            f"For US state/region: '{state_or_region}', reply with only the sales tax rate as a decimal number "
            "(e.g. 0.0725 for 7.25%). No explanation, no percent sign, just the number."
        )
        return self.say(prompt).strip()

    def get_next_state(self, current_state: str, user_message: str) -> str:
        """Determine next conversation state. Used by CLI flow."""
        prompt = (
            f"Current state: {current_state}. User said: {user_message}. "
            "Reply with ONLY one of: starting, getting_budget, getting_purpose, getting_preferences, "
            "getting_connection, getting_tax, getting_parts, getting_changes, finished. No other text."
        )
        return self.say(prompt).strip().lower()
