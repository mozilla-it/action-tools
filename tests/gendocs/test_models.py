import pytest

from action_tools.models import ActionInput


def test_required_input_without_default_or_example():
    with pytest.raises(
        ValueError, match="Required input without default must provide an example."
    ):
        ActionInput(
            description="This is a required input",
            required=True,
            default=None,
            example=None,
        )
