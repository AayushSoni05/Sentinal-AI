from fastapi import Depends, HTTPException

from app.auth.dependencies import get_current_user


def require_roles(
    allowed_roles: set[str]
):
    def role_checker(
        current_user=Depends(get_current_user)
    ):
        user_role = current_user.role.name

        if user_role == "Admin":
            return current_user

        if user_role not in allowed_roles:
            roles = ", ".join(sorted(allowed_roles))

            raise HTTPException(
                status_code=403,
                detail=f"One of these roles is required: {roles}"
            )

        return current_user

    return role_checker


require_maker = require_roles(
    {"Maker"}
)

require_checker = require_roles(
    {"Checker"}
)

require_admin = require_roles(
    {"Admin"}
)

require_maker_or_checker = require_roles(
    {"Maker", "Checker"}
)
require_internal_user = require_roles(
    {"Maker", "Checker"}
)