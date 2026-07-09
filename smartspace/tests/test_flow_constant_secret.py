from smartspace.models import FlowConstant


def test_secret_defaults_to_false():
    assert FlowConstant(value="hello").secret is False


def test_secret_can_be_set():
    constant = FlowConstant(value="ss://secret/my-key", secret=True)
    assert constant.secret is True
    assert constant.value == "ss://secret/my-key"


def test_existing_flows_without_the_field_deserialize_as_not_secret():
    # Backward compat: flow definitions saved before the field existed must load
    # with secret=False, so nothing already in the wild starts resolving.
    constant = FlowConstant.model_validate({"value": "ss://secret/my-key"})
    assert constant.secret is False


def test_round_trips_through_dump_and_validate():
    original = FlowConstant(value="ss://secret/my-key", secret=True)
    restored = FlowConstant.model_validate(original.model_dump(by_alias=True))
    assert restored.secret is True
    assert restored.value == original.value
