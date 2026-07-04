from dataclasses import dataclass
from typing import Callable

from fastapi import Depends, Header, HTTPException, status

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "owner": {"*"},
    "admin": {
        "model:read",
        "model:manage",
        "knowledge:read",
        "knowledge:manage",
        "agent:run",
        "agent:manage",
        "workflow:read",
        "workflow:manage",
        "prompt:read",
        "prompt:manage",
        "eval:run",
        "eval:read",
        "audit:read",
        "chat:run",
    },
    "operator": {
        "model:read",
        "knowledge:read",
        "knowledge:manage",
        "agent:run",
        "agent:manage",
        "workflow:read",
        "workflow:manage",
        "prompt:read",
        "prompt:manage",
        "eval:run",
        "eval:read",
        "audit:read",
        "chat:run",
    },
    "viewer": {"model:read", "knowledge:read", "agent:run", "audit:read", "chat:run", "workflow:read", "prompt:read", "eval:read"},
}


@dataclass(frozen=True)
class UserContext:
    tenant_id: int
    user_id: int
    role: str
    permissions: set[str]

    def can(self, permission: str) -> bool:
        return "*" in self.permissions or permission in self.permissions

    def to_dict(self) -> dict[str, object]:
        return {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "role": self.role,
            "permissions": sorted(self.permissions),
        }


async def get_current_context(
    x_tenant_id: int = Header(default=1, alias="X-Tenant-Id"),
    x_user_id: int = Header(default=1, alias="X-User-Id"),
    x_user_role: str = Header(default="admin", alias="X-User-Role"),
) -> UserContext:
    role = x_user_role.lower().strip() or "viewer"
    permissions = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["viewer"])
    return UserContext(tenant_id=x_tenant_id, user_id=x_user_id, role=role, permissions=set(permissions))


def require_permission(permission: str) -> Callable[[UserContext], UserContext]:
    async def dependency(context: UserContext = Depends(get_current_context)) -> UserContext:
        if not context.can(permission):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Missing permission: {permission}")
        return context

    return dependency
