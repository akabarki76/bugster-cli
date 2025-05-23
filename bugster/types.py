from typing import Literal, Optional, Union, Any
from pydantic import BaseModel


class Test(BaseModel):
    id: Optional[str] = None
    version: Optional[str] = None
    name: str
    task: str
    expected_result: str
    steps: Optional[list[str]] = None


class Credential(BaseModel):
    id: Optional[str] = None
    username: str
    password: str


class Config(BaseModel):
    base_url: str
    credentials: list[Credential]


class WebSocketMessage(BaseModel):
    action: str


class WebSocketInitTestMessage(WebSocketMessage):
    action: Literal["init_test"] = "init_test"
    test: Test
    config: Config


class ToolRequest(BaseModel):
    id: str
    name: str
    args: dict


class WebSocketStepResultMessage(WebSocketMessage):
    action: Literal["step_result"] = "step_result"
    job_id: str
    tool: ToolRequest
    status: Literal["success", "error"]
    output: str


class WebSocketStepRequestMessage(WebSocketMessage):
    action: Literal["step_request"] = "step_request"
    job_id: str
    tool: ToolRequest
    message: str


class TestResult(BaseModel):
    result: Literal["pass", "fail"]
    reason: str


class WebSocketCompleteMessage(WebSocketMessage):
    action: Literal["complete"] = "complete"
    result: TestResult


class NamedTestResult(TestResult):
    name: str
    time: Optional[float] = None
