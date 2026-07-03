import ipaddress
from typing import Any
from urllib.parse import urlparse

import httpx


class HTTPRequestTool:
    name = "http_request"
    description = "HTTP 请求工具，安全模式下访问允许的 http/https 地址并返回摘要。"
    args_schema = {"method": "string", "url": "string", "params": "object", "json": "object"}

    _blocked_hosts = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}
    _blocked_suffixes = (".local", ".internal", ".lan")
    _allowed_methods = {"GET", "POST"}

    async def run(self, args: dict[str, Any]) -> dict[str, Any]:
        method = str(args.get("method", "GET")).upper()
        url = str(args.get("url", "")).strip()
        self._validate_request(method, url)

        params = args.get("params") if isinstance(args.get("params"), dict) else None
        json_body = args.get("json") if isinstance(args.get("json"), dict | list) else None
        async with httpx.AsyncClient(timeout=10, follow_redirects=False) as client:
            response = await client.request(method, url, params=params, json=json_body)

        try:
            body: Any = response.json()
        except ValueError:
            body = response.text[:2000]

        return {
            "method": method,
            "url": str(response.url),
            "status_code": response.status_code,
            "ok": response.is_success,
            "content_type": response.headers.get("content-type", ""),
            "body": body,
            "source": "http_safe_mode",
        }

    def _validate_request(self, method: str, url: str) -> None:
        if method not in self._allowed_methods:
            raise ValueError("Only GET and POST are allowed in safe mode")
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Only http and https URLs are allowed")
        if not parsed.hostname:
            raise ValueError("URL hostname is required")
        hostname = parsed.hostname.lower()
        if hostname in self._blocked_hosts or hostname.endswith(self._blocked_suffixes):
            raise ValueError("Local or internal hosts are blocked")
        try:
            ip = ipaddress.ip_address(hostname)
        except ValueError:
            return
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            raise ValueError("Private, reserved or local IP addresses are blocked")
