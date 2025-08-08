from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator


class ActionInput(BaseModel):
    model_config = ConfigDict(extra="allow")

    description: Optional[str] = None
    required: Optional[bool] = False
    default: Optional[str] = None
    example: Optional[str] = None

    @model_validator(mode="after")
    def check_required_has_default_or_example(self) -> "ActionInput":
        if self.required and self.default is None and self.example is None:
            raise ValueError("Required input without default must provide an example.")
        return self


class ActionOutput(BaseModel):
    description: Optional[str] = None
    value: Optional[str] = None


class GitHubAction(BaseModel):
    name: str
    description: str
    inputs: dict[str, ActionInput] = {}
    outputs: dict[str, ActionOutput] = {}


class Resource(BaseModel):
    org: str
    repo: str
    subpath: str


class Workflow(Resource):
    pass


class Action(Resource):
    pass
