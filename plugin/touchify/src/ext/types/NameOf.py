import dis
import inspect
from functools import lru_cache


def nameof(_):
    frame = inspect.currentframe().f_back
    result = _nameof(frame.f_code, frame.f_lasti)
    return str(result)


@lru_cache()
def _nameof(code, offset):
    instructions = list(dis.get_instructions(code))
    (current_instruction_index, current_instruction), = (
        (index, instruction)
        for index, instruction in enumerate(instructions)
        if instruction.offset == offset
    )
    assert current_instruction.opname in ("CALL_FUNCTION", "CALL_METHOD"), "Did you call nameof in a weird way?"
    name_instruction = instructions[current_instruction_index - 1]
    assert name_instruction.opname.startswith("LOAD_"), "Argument must be a variable or attribute"
    return name_instruction.argrepr