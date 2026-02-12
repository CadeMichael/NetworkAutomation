from dataclasses import dataclass

@dataclass
class Router:
    index: int
    ips: str
    loopbacks: str
    user: str
    password: str
    secret: str
