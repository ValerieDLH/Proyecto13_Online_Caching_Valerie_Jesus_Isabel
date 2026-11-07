import random
import unittest

from src.analysis import (
    canonical_belady_example,
    competitive_ratio,
    detect_belady,
)
from src.cache_algorithms import simulate_fifo, simulate_lru, simulate_opt


class CacheAlgorithmsTest(unittest.TestCase):
    def setUp(self):
        self.sequence = [1, 2, 3, 1, 4, 2, 5]
        self.capacity = 3

    def test_fifo(self):
        result = simulate_fifo(self.sequence, self.capacity)
        self.assertEqual(result.hits, 2)
        self.assertEqual(result.misses, 5)
        self.assertEqual(result.replacements, 2)

    def test_lru(self):
        result = simulate_lru(self.sequence, self.capacity)
        self.assertEqual(result.hits, 1)
        self.assertEqual(result.misses, 6)
        self.assertEqual(result.replacements, 3)

    def test_opt(self):
        result = simulate_opt(self.sequence, self.capacity)
        self.assertEqual(result.hits, 2)
        self.assertEqual(result.misses, 5)
        self.assertEqual(result.replacements, 2)

    def test_opt_never_worse_than_fifo_or_lru_on_example(self):
        fifo = simulate_fifo(self.sequence, self.capacity)
        lru = simulate_lru(self.sequence, self.capacity)
        opt = simulate_opt(self.sequence, self.capacity)

        self.assertLessEqual(opt.misses, fifo.misses)
        self.assertLessEqual(opt.misses, lru.misses)

    def test_opt_never_worse_on_random_cases(self):
        rng = random.Random(2026)

        for _ in range(100):
            length = rng.randint(1, 60)
            universe = rng.randint(1, 12)
            capacity = rng.randint(1, 8)
            sequence = [rng.randrange(universe) for _ in range(length)]

            fifo = simulate_fifo(sequence, capacity)
            lru = simulate_lru(sequence, capacity)
            opt = simulate_opt(sequence, capacity)

            self.assertLessEqual(opt.misses, fifo.misses)
            self.assertLessEqual(opt.misses, lru.misses)

    def test_invalid_capacity(self):
        with self.assertRaises(ValueError):
            simulate_fifo([1, 2, 3], 0)

    def test_empty_sequence(self):
        result = simulate_lru([], 3)
        self.assertEqual(result.accesses, 0)
        self.assertEqual(result.miss_rate, 0.0)

    def test_competitive_ratio(self):
        self.assertEqual(competitive_ratio(10, 5), 2.0)
        self.assertEqual(competitive_ratio(0, 0), 1.0)

    def test_belady_canonical_example(self):
        sequence, capacities = canonical_belady_example()
        rows = detect_belady(sequence, capacities)

        self.assertEqual(rows[0]["capacity"], 3)
        self.assertEqual(rows[0]["fifo_misses"], 9)
        self.assertEqual(rows[1]["capacity"], 4)
        self.assertEqual(rows[1]["fifo_misses"], 10)
        self.assertTrue(rows[1]["belady_anomaly"])


if __name__ == "__main__":
    unittest.main()
