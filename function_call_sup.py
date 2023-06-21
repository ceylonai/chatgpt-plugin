from typing import Any, Dict, Optional

from pydantic.fields import Undefined
import inspect


def Query(  # noqa: N802
        default: Any = Undefined,
        *,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        required: bool = False,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        example: Any = Undefined,
        examples: Optional[Dict[str, Any]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        **extra: Any,
) -> Any:
    class QueryCls:
        def __init__(self, default: Any = Undefined, **kwargs):
            self.default = default
            self.__dict__.update(kwargs)

    return QueryCls(default,
                    alias=alias,
                    title=title,
                    required=required,
                    description=description,
                    gt=gt,
                    ge=ge,
                    lt=lt,
                    le=le,
                    min_length=min_length,
                    max_length=max_length,
                    regex=regex,
                    example=example,
                    examples=examples,
                    deprecated=deprecated,
                    include_in_schema=include_in_schema,
                    **extra)


def get_function_detail(func):
    _name = func.__name__
    _description = func.__doc__
    _detail = func.__defaults__
    inspect.getfullargspec(func)

    properties = {}
    required = []
    sig = inspect.signature(func)
    params = sig.parameters
    for name, param in params.items():
        query = param.default
        _type = type(query.default)

        if _type == str:
            _type = "string"
        elif _type == int:
            _type = "integer"
        elif _type == bool:
            _type = "boolean"
        elif _type == float:
            _type = "number"

        properties[name] = {
            "type": _type,
            "description": query.description,
        }

        if query.required:
            required.append(name)

    func_detail = {
        "name": _name,
        "description": _description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }
    return func_detail


def reg_functions(funcs: []):
    _functions = []
    _function_calls = {}
    for func in funcs:
        func_detail = get_function_detail(func)
        _functions.append(func_detail)
        _function_calls[func_detail["name"]] = func
    return _functions, _function_calls


def process_conversation(messages, function_details, function_calls, model="gpt-3.5-turbo-0613"):
    import os
    import json
    import openai
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    # Step 1: send the conversation and available functions to GPT

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        functions=function_details,
        function_call="auto",  # auto is default, but we'll be explicit
    )
    response_message = response["choices"][0]["message"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = function_calls
        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = fuction_to_call(
            location=function_args.get("location"),
            unit=function_args.get("unit"),
        )

        # Step 4: send the info on the function call and function response to GPT
        messages.append(response_message)  # extend conversation with assistant's reply
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response
        second_response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
        )  # get a new response from GPT where it can see the function response
        return second_response
"""

'''py
import json
from external_services.open_ai_func import Query, reg_functions, process_conversation

from dotenv import load_dotenv

load_dotenv(".env")


def get_current_weather_func_1(location: str = Query(
    default="San Francisco",
    description="The city and state, e.g. San Francisco, CA",
    title="City",
    example="San Francisco",
    required=True,
), unit: str = Query(
    default="celsius",
    description="The unit of temperature",
    title="Unit",
    example="celsius",
)):
    """Get current weather"""
    weather_info = {
        "location": location,
        "temperature": "72",
        "unit": unit,
        "forecast": ["sunny", "windy"],
    }
    return json.dumps(weather_info)


functions, function_calls = reg_functions([get_current_weather_func_1, ])
_messages = [{"role": "user", "content": "What's the weather like in Boston?"}]
res = process_conversation(_messages, functions, function_calls)
print(res)


'''


"""
