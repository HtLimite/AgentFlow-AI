from typing import Any
from urllib.parse import urlparse


class HTTPRequestTool:
    name = "http_request"
    description = "HTTP 请求工具安全演示版。"
    args_schema = {"method": "string", "url": "string"}

    _blocked_hosts = {"localhost", "127.0.0.1", "0.0.0.0"}

    async def run(self, args: dict[str, Any]) -> dict[str, Any]:
        method = str(args.get("method", "GET")).upper()
        url = str(args.get("url", ""))
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Only http and https URLs are allowed")
        if parsed.hostname in self._blocked_hosts:
            raise ValueError("Local addresses are blocked")
        return {"method": method, "url": url, "status_code": 200, "body": {"message": "demo response"}}
