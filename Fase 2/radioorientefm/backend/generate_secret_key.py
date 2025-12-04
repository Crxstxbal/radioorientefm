"""script para generar una secret_key segura para django. ejecuta este script y copia el resultado a tu archivo .env uso: python generate_secret_key.py"""

from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    secret_key = get_random_secret_key()
    print("\n" + "="*70)
    print("NUEVA SECRET_KEY GENERADA")
    print("="*70)
    print(f"\nSECRET_KEY={secret_key}")
    print("\n" + "="*70)
    print("Copia la línea de arriba a tu archivo .env")
    print("IMPORTANTE: NO compartas esta clave con nadie ni la subas a git")
    print("="*70 + "\n")
