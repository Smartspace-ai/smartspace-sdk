from typing import Any

from lark import Lark, Token, Transformer

#
# ------------------- GRAMMAR -------------------
#
grammar = r"""
VALUE.2: /(?i)value/
LEN.2:   /(?i)len/

LPAR: "("
RPAR: ")"
DOT: "."

%import common.CNAME -> BASE_CNAME
CNAME: BASE_CNAME

%import common.INT
%import common.FLOAT
%import common.WS
%ignore WS

NUMBER: INT | FLOAT

STRING: /'[^']*'/ | /"[^"]*"/

NONE: /(?i)(none|null)/
TRUE: /(?i)true/
FALSE: /(?i)false/

?literal: list_literal
        | dict_literal

?list_literal: "[" [expr_list] "]" | "[]"
?expr_list: expr ("," expr)*

?dict_literal: "{" [pair_list] "}" | "{}"
?pair_list: pair ("," pair)*
?pair: STRING ":" expr

?start: expr

?expr:
    | expr "and"i expr               -> and_
    | expr "or"i expr                -> or_
    | expr OPERATOR expr             -> compare
    | expr "is"i "not"i NONE         -> is_not_none
    | expr "is"i "not"i FALSE        -> is_not_false
    | expr "in"i expr                -> in_
    | expr "not"i "in"i expr         -> not_in_
    | LEN LPAR expr RPAR OPERATOR NUMBER -> length_compare
    | value_attr
    | NUMBER                         -> number
    | STRING                         -> string
    | NONE                           -> none_
    | TRUE                           -> true_
    | FALSE                          -> false_
    | dict_literal                          -> dict_literal
    | list_literal                          -> list_literal
    | LPAR expr RPAR                 -> parens

OPERATOR: "==" | "!=" | "<>" | ">" | "<" | ">=" | "<=" | "~="

?value_attr: VALUE property_list
?property_list: (dot_property | bracket_index)*

dot_property: DOT CNAME
bracket_index: "[" NUMBER "]"
"""


class ConditionEvaluator(Transformer):
    """
    Walks the parse tree from the grammar and evaluates expressions
    against the provided `context` dict (or any Python object).
    """

    def __init__(self, context: Any):
        super().__init__()
        self.context = context  # The "value" in expressions

    #
    # ----- Logical operators -----
    #
    def and_(self, args):
        return args[0] and args[1]

    def or_(self, args):
        return args[0] or args[1]

    #
    # ----- "is not none", "is not false" -----
    #
    def is_not_none(self, args):
        # e.g. value.user.name is not none
        return args[0] is not None

    def is_not_false(self, args):
        # e.g. value.user.profile.active is not false
        return args[0] is not False

    #
    # ----- "in" / "not in" -----
    #
    def in_(self, args):
        """
        expr "in" expr
        e.g. value in [10, 15, 20]
             value.user.name in "Alice"
        """
        left, right = args
        return self._check_membership(left, right)

    def not_in_(self, args):
        left, right = args
        return not self._check_membership(left, right)

    def _check_membership(self, left, container):
        """
        Implement "left in container" for list, dict, str, etc.
        """
        if isinstance(container, list):
            container = [i.value if isinstance(i, Token) else i for i in container]

        if isinstance(container, dict):
            container = {
                k.value if isinstance(k, Token) else k: v.value
                if isinstance(v, Token)
                else v
                for k, v in container.items()
            }

        if isinstance(container, dict):
            return left in container
        elif isinstance(container, (list, str)):
            return left in container
        # You can decide how to handle other types:
        return False

    #
    # ----- len(...) OP NUMBER -----
    #
    def length_compare(self, args):
        """
        e.g. len(value.items) == 3
        """
        # parse layout: [Token(LEN), Token(LPAR), expr, Token(RPAR), operator, number]
        container, operator, number = args[2], args[4], args[5]

        # Convert operator, number from Token if needed
        if isinstance(operator, Token):
            operator = operator.value
        if isinstance(number, Token):
            number = float(number.value)

        if not isinstance(number, float):
            number = float(number)

        # container could be str, list, dict
        if not isinstance(container, (list, dict, str)):
            return False

        left_side = len(container)
        return self.apply_operator(left_side, operator, number)

    #
    # ----- Comparisons (expr OPERATOR expr) -----
    #
    def compare(self, args):
        """
        e.g. value.user.age > 18
             "abc" ~= "b"
             'foo' != 'bar'
             value.items[0] <= 10
             value == {"test": 1}
        """
        left, operator, right = args
        return self.apply_operator(left, operator, right)

    #
    # ----- Parentheses -----
    #
    def parens(self, args):
        return args[0]

    #
    # ----- value_attr (like value.user.age, etc.) -----
    #
    def value_attr(self, children):
        """
        children might be [Token('VALUE','value'), property_list([...])]
        If no property_list, it's just 'value'.
        """
        if len(children) == 1:
            # means there's no property_list, so it's just 'value'
            return self.context
        else:
            path_list = children[1]  # output from property_list
            return self._get_nested(path_list)

    def property_list(self, children):
        """
        property_list is a sequence of dot_property or bracket_index subtrees,
        each returning something like ["user"] or ["2"].
        We'll flatten them into one path list, e.g. ["user","age"].
        """
        path = []
        for child in children:
            path.extend(child)
        return path

    def dot_property(self, tokens):
        # tokens = [Token('DOT','.'), Token('CNAME','user')]
        return [tokens[1].value]

    def bracket_index(self, tokens):
        # tokens = [Token('[','['), Token('NUMBER','2'), Token(']',']')]
        if len(tokens) > 1:
            return [tokens[1].value]
        else:
            return [tokens[0].value]

    def _get_nested(self, path_list):
        """
        Actually retrieve the nested object from self.context,
        e.g. path_list = ["user","age"] or ["items","2"].
        """
        obj = self.context
        for part in path_list:
            if isinstance(obj, dict):
                obj = obj.get(part)
            elif isinstance(obj, list) and part.isdigit():
                idx = int(part)
                if 0 <= idx < len(obj):
                    obj = obj[idx]
                else:
                    obj = None
            else:
                # last resort: attribute access
                obj = getattr(obj, part, None)
        return obj

    #
    # ----- Literal lists & dicts -----
    #
    def list_literal(self, children):
        """
        list_literal: "[" [expr_list] "]"
        children might be empty (no expr_list) or one child which is expr_list
        """
        if not children:
            return []  # empty list, e.g. []
        else:
            # children[0] is the result of expr_list
            if isinstance(children[0], list) and len(children) == 1:
                return children[0]
            return children

    def expr_list(self, children):
        """
        expr_list: expr ("," expr)* -> a list of expressions
        """
        return children  # e.g. [expr1, expr2, expr3, ...]

    def dict_literal(self, children):
        """
        dict_literal: "{" [pair_list] "}"
        children might be empty or one child which is pair_list
        """
        if not children:
            return {}
        else:
            d = {}
            pairs = children if isinstance(children, list) else children.items()
            for pair in pairs:
                # each pair is (key, value)
                if isinstance(pair, dict):
                    d.update(pair)
                else:
                    k, v = pair
                    d[k] = v
            return d
            # children[0] is the pair_list

    def pair_list(self, children):
        """
        pair_list: pair ("," pair)*
        We'll merge them into a single dict
        """
        d = {}
        for pair in children:
            # each pair is (key, value)
            k, v = pair
            d[k] = v
        return d

    def pair(self, children):
        """
        pair: string ":" expr
        So children = [string_value, expr_value]
        """
        key = self.string(
            [children[0].value if isinstance(children[0], Token) else children[0]]
        )
        val = children[1].value if isinstance(children[1], Token) else children[1]
        return (key, val)

    #
    # ----- Terminal tokens: string, none, true, false, number -----
    #
    def string(self, args):
        """
        Convert e.g. "'Ali'" -> "Ali"
        """
        s = args[0]
        if (s.startswith("'") and s.endswith("'")) or (
            s.startswith('"') and s.endswith('"')
        ):
            return s[1:-1]
        return s

    def none_(self, _):
        return None

    def true_(self, _):
        return True

    def false_(self, _):
        return False

    def number(self, args):
        raw = args[0]
        if "." in raw:
            return float(raw)
        return int(raw)

    #
    # ----- Core operator logic -----
    #
    def apply_operator(self, left, operator, right):
        """
        We have standard operators + "<>" for != + "~=" for substring match.
        """
        # If either side is None, turn it into "" for string comparisons:
        if left is None:
            left = ""
        if right is None:
            right = ""

        # "~=" => substring check: str(left) contains str(right)
        if operator == "~=":
            return str(right) in str(left)

        # If it's == or != and either side is a string, do str compare
        if operator in ("==", "!=", "<>"):
            if isinstance(left, str) or isinstance(right, str):
                left = str(left)
                right = str(right)

        # Numeric comparisons
        if operator in (">", "<", ">=", "<=", "!=", "==", "<>"):
            # If either side is numeric, attempt float conversion
            if any(isinstance(x, (int, float)) for x in (left, right)):
                try:
                    left = float(left)
                    right = float(right)
                except ValueError:
                    return False

        # Define standard operators
        ops = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            "<>": lambda a, b: a != b,  # alternate not-equal
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
        }
        return ops[operator](left, right)


_parser = None


def evaluate_expression(condition: str, value: Any = None):
    """
    Main entry point: parse the condition string,
    then evaluate it against the given value or dict context.
    """
    global _parser
    if _parser is None:
        evaluate_expression = Lark(grammar, parser="lalr")
    tree = evaluate_expression.parse(condition)
    return ConditionEvaluator(value).transform(tree)


expression_tooltip = """Use value to reference your data (dict/list/etc.), e.g. value.user.age > 18.

Supports and, or, and operators like ==, !=, <, >, >=, <=, ~= (substring).

Check nested fields (value.user.profile.active is not false), lengths (len(value.items) == 3), and membership ('read' in value.user.permissions).

Literal lists/dicts let you do value in [10, null, "foo"] or value == {"test": 1}.

none|null|true|false are parsed as Python None|None|True|False"""

#
# ------------------- EXAMPLE & TESTS -------------------
#
if __name__ == "__main__":
    example_data = {
        "user": {
            "name": "Alice",
            "age": 25,
            "permissions": ["read", "write", "admin"],
            "profile": {"active": True},
        },
        "items": [10, 20, 30],
    }
    assert evaluate_expression("value == [{'text': 'test'}]", [{"text": "test"}])
    assert evaluate_expression("value in [10, 15, 20]", 10)  # => True

    # Basic tests
    assert evaluate_expression("value is not none", example_data)
    assert evaluate_expression("value.user.age > 18", example_data)
    assert evaluate_expression("value.user.name is not none", example_data)
    assert evaluate_expression("'read' in value.user.permissions", example_data)
    assert evaluate_expression("'delete' not in value.user.permissions", example_data)
    assert evaluate_expression("value.items[0] == 10", example_data)
    assert evaluate_expression("value.items[1] > 15", example_data)
    assert evaluate_expression("value.user.profile.active is not False", example_data)
    assert evaluate_expression("len(value.user.permissions) > 2", example_data)
    assert evaluate_expression("len(value.items) == 3", example_data)
    assert evaluate_expression("value.items[2] <= 30", example_data)
    assert evaluate_expression("value.user.age != 30", example_data)
    assert not evaluate_expression("value.user.age < 20", example_data)
    assert not evaluate_expression("value.user.nonexistent is not none", example_data)
    assert not evaluate_expression("value.items[100] > 10", example_data)

    # Alternate not-equal "<>"
    assert evaluate_expression("value.user.age <> 26", example_data)  # 25 != 26 => True

    # Substring operator "~="
    assert evaluate_expression(
        'value.user.name ~= "Ali"', example_data
    )  # "Alice" contains "Ali"
    assert not evaluate_expression('value.user.name ~= "icex"', example_data)

    # none/null/true/false
    assert evaluate_expression("value.user.age != none", example_data)
    assert evaluate_expression("value.user.age != null", example_data)
    assert evaluate_expression("value.user.profile.active == true", example_data)
    assert not evaluate_expression("value.user.profile.active == false", example_data)

    # "value.nobody" => None => == none => True
    assert evaluate_expression("value.nobody == none", example_data)

    # Quoted strings are stripped
    assert evaluate_expression('"Ali" == "Ali"', example_data)
    assert not evaluate_expression('"Ali" == "alice"', example_data)

    #
    # ---------- NEW TESTS for list/dict literal ----------
    #

    # 1) Membership in a literal list
    assert evaluate_expression("value in [10, 15, 20]", 10)  # => True
    assert not evaluate_expression("value in [10, 15, 20]", 5)  # => False
    # Mixed items including strings, none, etc.
    assert evaluate_expression("value in ['abc', none, 10]", 10)  # => True
    assert evaluate_expression(
        "value in ['abc', null, 10]", 10
    )  # => True, "null" => None

    # 2) Compare to literal dict
    # e.g. "value == {'test': 1}"
    my_dict = {"test": 1}
    assert evaluate_expression('value == {"test": 1}', my_dict)  # => True
    assert not evaluate_expression("value == {'test': 2}", my_dict)  # => False
    # Nested dict & lists
    big_dict = {"test": 1, "nested": [3, 4, {"key": False}]}
    assert evaluate_expression(
        "value == {'test':1, 'nested': [3,4, {'key':false}]}", big_dict
    )

    # 3) "in" a dict means "left in dict_keys"
    assert evaluate_expression("value in {'test':1, \"nested\":2}", "nested")  # => True
    assert not evaluate_expression("value in {'test':1, 'nested':2}", "none")

    assert evaluate_expression("'test' == 'test'")
    assert not evaluate_expression("'test' in 'tes_t'")

    assert not evaluate_expression("value not in [false, null, [], 0, '', {}]", None)
    assert not evaluate_expression("value not in [false, null, [], 0, '', {}]", False)
    assert not evaluate_expression("value not in [false, null, [], 0, '', {}]", "")
    assert not evaluate_expression("value not in [false, null, [], 0, '', {}]", 0)
    assert not evaluate_expression("value not in [false, null, [], 0, '', {}]", [])
    assert not evaluate_expression("value not in [false, null, [], 0, '', {}]", {})
    assert not evaluate_expression("value", None)
    assert not evaluate_expression("value", False)
    assert not evaluate_expression("value", "")
    assert not evaluate_expression("value", 0)
    assert not evaluate_expression("value", [])
    assert not evaluate_expression("value", {})
    assert evaluate_expression("value not in [false, null, [], 0, '', {}]", 1)
    assert evaluate_expression("value not in [false, null, [], 0, '', {}]", "test")
    assert evaluate_expression("value not in [false, null, [], 0, '', {}]", True)
    assert evaluate_expression("value not in [false, null, [], 0, '', {}]", [0])
    assert evaluate_expression("value not in [false, null, [], 0, '', {}]", {"test": 1})

    print("All tests passed!")
