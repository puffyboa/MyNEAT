"""
Contains configuration for genomes, species, populations, etc., and generators for float, bool, and string values.
Also contains counters for id's and innovation numbers.
Configuration parameters themselves are largely copied from NEAT-Python.
"""

from itertools import count
from dataclasses import dataclass
import random
from .math_util import mean


def clamp(value, low, high):
    return max(min(value, high), low)


@dataclass
class FloatConfig:
    init_mean: float
    init_stdev: float
    max_value: float
    min_value: float
    mutate_power: float
    mutate_rate: float
    replace_rate: float
    init_type: str = "gauss"

    def new(self):
        if self.init_type == "gauss":
            return clamp(random.gauss(self.init_mean, self.init_stdev), self.min_value, self.max_value)
        if self.init_type == "uniform":
            min_value = max(self.min_value, (self.init_mean - (2 * self.init_stdev)))
            max_value = min(self.max_value, (self.init_mean + (2 * self.init_stdev)))
            return random.uniform(min_value, max_value)

    def mutate(self, value):
        # mutate_rate is usually no lower than replace_rate, and frequently higher -
        # so put first for efficiency
        r = random.random()
        if r < self.mutate_rate:
            return clamp(value + random.gauss(0.0, self.mutate_power), self.min_value, self.max_value)

        if r < self.replace_rate + self.mutate_rate:
            return self.new()

        return value


@dataclass
class BoolConfig:
    mutate_rate: float
    default: bool = None
    rate_to_true_add: float = 0.0
    rate_to_false_add: float = 0.0

    def new(self):
        return bool(random.random() < 0.5) if self.default is None else self.default

    def mutate(self, value):
        if self.mutate_rate > 0:
            # The mutation operation *may* change the value but is not guaranteed to do so
            if random.random() < self.mutate_rate:
                return random.random() < 0.5
        return value


@dataclass
class StringConfig:
    options: [str]
    mutate_rate: float
    default: str = None

    def new(self):
        if self.default is not None:
            return self.default
        return random.choice(self.options)

    def mutate(self, value):
        if self.mutate_rate > 0:
            if random.random() < self.mutate_rate:
                return random.choice(self.options)
        return value


@dataclass
class BaseConfig:
    """
    Contains configuration and counters for a simulation
    """

    # node activation options
    activation_config = StringConfig(
        default="tanh",
        mutate_rate=0.05,
        options=["sigmoid", "tanh", "sin", "gauss", "identity"]
    )

    # node aggregation options
    aggregation_config = StringConfig(
        default="sum",
        mutate_rate=0.05,
        options=["sum", "product", "max", "min"]
    )

    # node bias options
    bias_config = FloatConfig(
        init_mean=0.0,
        init_stdev=1.0,
        max_value=30.0,
        min_value=-30.0,
        mutate_power=0.5,
        mutate_rate=0.7,
        replace_rate=0.1
    )

    # genome compatibility options
    compatibility_disjoint_coefficient = 1.0  # c2, takes the place of both c1 and c2
    compatibility_weight_coefficient = 0.5  # c3

    # connection add/remove rates
    conn_add_prob = 0.5
    conn_delete_prob = 0.5

    # connection enable options
    enabled_config = BoolConfig(
        default=True,
        mutate_rate=0.01
    )

    feed_forward = False  # Not used
    initial_connection = "full"  # Not used

    # node add/remove rates
    node_add_prob = 0.2
    node_delete_prob = 0.2

    # network parameters
    num_hidden = 0  # Not used
    num_inputs = 2
    num_outputs = 1

    # node response options
    response_config = FloatConfig(
        init_mean=1.0,
        init_stdev=0.0,
        max_value=30.0,
        min_value=-30.0,
        mutate_power=0.0,
        mutate_rate=0.0,
        replace_rate=0.0
    )

    # connection weight options
    weight_config = FloatConfig(
        init_mean=0.0,
        init_stdev=1.0,
        max_value=30.0,
        min_value=-30.0,
        mutate_power=0.5,
        mutate_rate=0.8,
        replace_rate=0.1
    )

    # structural mutations
    single_structural_mutation = False  # If enabled, only one structural mutation per genome per "generation"
    structural_mutation_surer = False  # If enabled, perform alternative structural mutations on failure

    # dynamic compatibility threshold
    compat_threshold_initial = 3.0  # initial compatibility threshold value
    compat_threshold_modifier = 0.1  # amount by which to adjust the compat threshold if num of species is off-target
    compat_threshold_min = 0.1  # minimum value of compatibility threshold
    target_num_species = 50  # dynamic compatibility threshold used to maintain this target

    # stagnation
    species_fitness_func = mean  # how to measure fitness of a species based on its members' fitness (for stagnation)
    max_stagnation = 15  # how long before a species can be removed for not improving its species-fitness (15)
    species_elitism = 0  # number of species with highest species-fitness are protected from stagnation
    reset_on_extinction = True  # init new population if all species simultaneously become extinct due to stagnation

    # reproduction NOT IMPLEMENTED
    elitism = 0  # The number of most-fit individuals in each species to be preserved as-is from one generation to next
    survival_threshold = 0.2  # The fraction of members for each species allowed to reproduce each generation
    min_species_size = 2  # The minimum number of genomes per species after reproduction

    pop_size = 150

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)

        self.node_key_indexer = count()
        # By convention, input pins have negative keys, and the output
        # pins have keys 0,1,...
        self.input_keys = [-i - 1 for i in range(self.num_inputs)]
        self.output_keys = [i for i in range(self.num_outputs)]


