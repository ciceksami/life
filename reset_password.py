#!/usr/bin/env python3

import hashlib
import secrets
import getpass
import redis
import sys


def hash_password(password):
    iterations = 120000
    salt = secrets.token_bytes(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations
    )

    return "pbkdf2_sha256${}${}${}".format(
        iterations,
        salt.hex(),
        digest.hex()
    )


def main():
    print("=" * 46)
    print("       AVATAR LIFE #2017 - ADMIN")
    print("           ŞİFRE SIFIRLAMA")
    print("=" * 46)

    try:
        r = redis.Redis(decode_responses=True)
        r.ping()
    except Exception as e:
        print("\n[HATA] Redis bağlantısı kurulamadı:")
        print(e)
        sys.exit(1)

    uid = input("\nOyuncu ID: ").strip()

    if not uid.isdigit():
        print("\n[HATA] Oyuncu ID sadece rakamlardan oluşmalıdır.")
        return

    email = r.get(f"uid:{uid}:email")

    if not email:
        print(f"\n[HATA] Oyuncu #{uid} için kayıtlı e-posta bulunamadı.")
        return

    print("\nHesap bulundu")
    print("-" * 46)
    print(f"Oyuncu ID : {uid}")
    print(f"E-posta   : {email}")
    print("-" * 46)

    password = getpass.getpass("\nYeni şifre: ")
    password_repeat = getpass.getpass("Yeni şifre tekrar: ")

    if password != password_repeat:
        print("\n[HATA] Şifreler eşleşmiyor.")
        return

    if len(password) < 6:
        print("\n[HATA] Şifre en az 6 karakter olmalıdır.")
        return

    if len(password) > 128:
        print("\n[HATA] Şifre en fazla 128 karakter olabilir.")
        return

    confirm = input(
        f"\nOyuncu #{uid} için web şifresi değiştirilsin mi? [E/h]: "
    ).strip().lower()

    if confirm not in ("", "e", "evet", "y", "yes"):
        print("\nİşlem iptal edildi.")
        return

    password_hash = hash_password(password)

    r.set(f"uid:{uid}:webpass", password_hash)

    print("\n" + "=" * 46)
    print("✓ ŞİFRE BAŞARIYLA DEĞİŞTİRİLDİ")
    print("=" * 46)
    print(f"Oyuncu ID : {uid}")
    print(f"E-posta   : {email}")
    print("\nOyuncu artık yeni şifresiyle giriş yapabilir.")


if __name__ == "__main__":
    main()
