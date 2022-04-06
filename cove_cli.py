import json
import sys
from argparse import ArgumentParser, Namespace
from datetime import datetime
from inspect import getfullargspec
from typing import Any, Callable, Dict, TextIO, get_args

from boto3 import Session
from botocove import CoveOutput, cove  # type: ignore[import]
from typing_inspect import is_generic_type, is_optional_type  # type: ignore[import]


class Encoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Exception):
            return repr(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def main() -> None:
    cove_args = get_cove_arg_parser().parse_args()
    cove_func = make_cove_func(sys.stdin.read(), cove_args)
    result = cove_func()
    dump_json(result, sys.stdout)


# Inspired by sqlite_utils' _compile_code.
def make_cove_func(body: str, cove_args: Namespace) -> Callable[..., CoveOutput]:

    body = body if body else "pass"

    header = "def func(session: Session):"
    func_source = "\n".join([header] + [f"    {line}" for line in body.splitlines()])

    code = compile(source=func_source, filename="<string>", mode="exec")

    locals: Dict[str, Any] = {}
    exec(code, None, locals)
    func = locals["func"]

    # TODO: Fix cove typing.
    return cove(  # type: ignore[no-any-return]
        func, **{k: v for k, v in vars(cove_args).items() if v is not None}
    )


def dump_json(result: CoveOutput, file: TextIO) -> None:
    json.dump(result, file, indent=4, cls=Encoder)


def get_cove_arg_parser() -> ArgumentParser:
    spec = getfullargspec(cove)
    parser = ArgumentParser()

    for arg in spec.kwonlyargs:
        hint = spec.annotations[arg]
        if is_optional_type(hint):
            type_arg = get_args(hint)[0]
            if is_generic_type(type_arg):
                type_arg = get_args(type_arg)[0]
                nargs = "*"
            else:
                nargs = "?"
        else:
            type_arg = hint
        print(f"{arg=} {hint=} {type_arg=}", file=sys.stderr)
        parser.add_argument(f"--{arg}", type=type_arg, nargs=nargs)

    return parser


if __name__ == "__main__":
    main()
