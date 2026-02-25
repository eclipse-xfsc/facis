"""
Seeded deterministic random number generator wrapper.

Ensures reproducible simulations with the same seed.
"""

from __future__ import annotations

import hashlib
import struct
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.random import Generator


class DeterministicRNG:
    """
    Wrapper for deterministic random generation.

    Provides reproducible random number generation based on a seed value.
    Different entities produce different sequences using entity-based sub-seeds.
    """

    def __init__(self, seed: int = 12345) -> None:
        """
        Initialize the deterministic RNG with a seed.

        Args:
            seed: Base seed value for reproducibility.
        """
        self._base_seed = seed
        self._rng: Generator = np.random.default_rng(seed)

    @property
    def seed(self) -> int:
        """Return the base seed value."""
        return self._base_seed

    def get_entity_rng(self, entity_id: str) -> Generator:
        """
        Get a deterministic RNG for a specific entity.

        The entity RNG produces unique but reproducible sequences
        for each entity while using the same base seed.

        Args:
            entity_id: Unique identifier for the entity.

        Returns:
            A new Generator seeded deterministically from base seed + entity_id.
        """
        entity_seed = self._compute_entity_seed(entity_id)
        return np.random.default_rng(entity_seed)

    def get_timestamp_rng(self, entity_id: str, timestamp_ms: int) -> Generator:
        """
        Get a deterministic RNG for a specific entity at a specific timestamp.

        Same seed + entity + timestamp always produces identical values.

        Args:
            entity_id: Unique identifier for the entity.
            timestamp_ms: Unix timestamp in milliseconds.

        Returns:
            A new Generator seeded deterministically from seed + entity + timestamp.
        """
        combined_seed = self._compute_timestamp_seed(entity_id, timestamp_ms)
        return np.random.default_rng(combined_seed)

    def _compute_entity_seed(self, entity_id: str) -> int:
        """
        Compute a deterministic seed for an entity.

        Args:
            entity_id: Unique identifier for the entity.

        Returns:
            A deterministic seed value derived from base seed and entity_id.
        """
        hash_input = f"{self._base_seed}:{entity_id}".encode()
        hash_bytes = hashlib.sha256(hash_input).digest()
        return struct.unpack(">Q", hash_bytes[:8])[0]

    def _compute_timestamp_seed(self, entity_id: str, timestamp_ms: int) -> int:
        """
        Compute a deterministic seed for an entity at a specific timestamp.

        Args:
            entity_id: Unique identifier for the entity.
            timestamp_ms: Unix timestamp in milliseconds.

        Returns:
            A deterministic seed value derived from base seed, entity_id, and timestamp.
        """
        hash_input = f"{self._base_seed}:{entity_id}:{timestamp_ms}".encode()
        hash_bytes = hashlib.sha256(hash_input).digest()
        return struct.unpack(">Q", hash_bytes[:8])[0]

    def random(self) -> float:
        """Generate a random float in [0.0, 1.0)."""
        return float(self._rng.random())

    def uniform(self, low: float, high: float) -> float:
        """Generate a random float in [low, high)."""
        return float(self._rng.uniform(low, high))

    def normal(self, mean: float = 0.0, std: float = 1.0) -> float:
        """Generate a random float from normal distribution."""
        return float(self._rng.normal(mean, std))

    def integers(self, low: int, high: int) -> int:
        """Generate a random integer in [low, high)."""
        return int(self._rng.integers(low, high))

    def choice(self, items: list) -> object:
        """Choose a random item from a list."""
        return self._rng.choice(items)

    def reset(self) -> None:
        """Reset the RNG to its initial state."""
        self._rng = np.random.default_rng(self._base_seed)
