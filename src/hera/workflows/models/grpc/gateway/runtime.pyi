from ...google import protobuf as protobuf
from hera.shared._base_model import BaseModel as BaseModel
from typing import List, Optional

class Error(BaseModel):
    code: Optional[int]
    details: Optional[List[protobuf.Any]]
    error: Optional[str]
    message: Optional[str]

class StreamError(BaseModel):
    details: Optional[List[protobuf.Any]]
    grpc_code: Optional[int]
    http_code: Optional[int]
    http_status: Optional[str]
    message: Optional[str]
