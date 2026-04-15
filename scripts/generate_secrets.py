#!/usr/bin/env python3
import secrets


def main() -> None:
    print(f"GF_SECURITY_ADMIN_PASSWORD={secrets.token_urlsafe(24)}")
    print(f"APP_HMAC_KEY={secrets.token_hex(32)}")


if __name__ == "__main__":
    main()
