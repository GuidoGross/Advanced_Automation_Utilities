import random
import math
import os

def _apply_variation(base_value, variation):
    if variation <= 0: return base_value
    return base_value + random.uniform(-base_value * variation, base_value * variation)

def _validate_between_range(minimum = 0, maximum = math.inf, **kwargs):
    for name, value in kwargs.items():
        if value is None: continue
        if not (minimum <= value <= maximum):
            formatted_name = name.replace("_", " ").capitalize()
            match (minimum, maximum):
                case (0, math.inf):
                    raise ValueError(f"{formatted_name} cannot be negative.")
                case (1, math.inf):
                    raise ValueError(f"{formatted_name} must be greater than or equal to 1.")
                case (_, math.inf):
                    raise ValueError(f"{formatted_name} must be greater than or equal to {minimum}.")
                case _: raise ValueError(f"{formatted_name} must be between {minimum} and {maximum}.")

def _validate_options(value, valid_options, name = "Option"):
    if value not in valid_options:
        options = ", ".join([f"\"{option}\"" for option in valid_options])
        raise ValueError(f"Invalid {name.lower()}. Valid options: {options}.")

def _validate_file_exists(file_path, name = "File"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{name} \"{file_path}\" does not exist or could not be found.")

def _validate_region(region):
    if region is not None:
        if len(region) != 4:
            raise ValueError("Region must be a tuple of 4 elements (left, top, right, bottom).")
        if region[0] >= region[2] or region[1] >= region[3]:
            raise ValueError("Region right and bottom must be greater than left and top respectively.")