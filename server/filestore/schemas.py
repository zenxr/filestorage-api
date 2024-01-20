import dataclasses

@dataclasses.dataclass
class CreateBucketRequest:
    path: str
    bucket_id: int

@dataclasses.dataclass
class CreateFileRequest:
    path: str
    bucket_id: int
