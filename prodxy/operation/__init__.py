from .judge_func import JudgePrimitives
from .llm_request import LLMRequest
from .relative_time import RelativeTimePrimitives
from .value_generator import ValueGeneratorPrimitives

OperationMap = {
    "judge:equal": JudgePrimitives.equal,
    "judge:include": JudgePrimitives.include,
    "llm:request": LLMRequest.call,
    "relative:date": RelativeTimePrimitives.calculate_date,
    "relative:time": RelativeTimePrimitives.calculate_time,
    "relative:datetime": RelativeTimePrimitives.calculate_datetime,
    "relative:compare": RelativeTimePrimitives.compare_datetime,
    "valgen:enum": ValueGeneratorPrimitives.enum,
    "valgen:range": ValueGeneratorPrimitives.range,
    "valgen:date": ValueGeneratorPrimitives.date,
    "valgen:time": ValueGeneratorPrimitives.time,
    "condition:exist": lambda x: True if x else False,
    "condition:identity": lambda x: x,
}

    
