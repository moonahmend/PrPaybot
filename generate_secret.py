#!/usr/bin/env python3
"""
Secret Key Generator for PrBot_Pay Admin Panel
This script generates secure random secret keys for Flask sessions
"""

import secrets
import string
import argparse

def generate_secret_key(length=32):
    """Generate a secure random secret key"""
    return secrets.token_urlsafe(length)

def generate_hex_key(length=32):
    """Generate a hex-based secret key"""
    return secrets.token_hex(length)

def generate_custom_key(length=32, include_symbols=True):
    """Generate a custom secret key with specified characters"""
    chars = string.ascii_letters + string.digits
    if include_symbols:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    return ''.join(secrets.choice(chars) for _ in range(length))

def main():
    parser = argparse.ArgumentParser(description='Generate secure secret keys for PrBot_Pay')
    parser.add_argument('--count', '-c', type=int, default=1, help='Number of keys to generate (default: 1)')
    parser.add_argument('--length', '-l', type=int, default=32, help='Length of the key (default: 32)')
    parser.add_argument('--type', '-t', choices=['urlsafe', 'hex', 'custom'], default='urlsafe', 
                       help='Type of key to generate (default: urlsafe)')
    parser.add_argument('--format', '-f', choices=['env', 'plain'], default='env',
                       help='Output format (default: env)')
    
    args = parser.parse_args()
    
    print("🔐 PrBot_Pay Secret Key Generator")
    print("=" * 40)
    
    for i in range(args.count):
        if args.type == 'urlsafe':
            key = generate_secret_key(args.length)
        elif args.type == 'hex':
            key = generate_hex_key(args.length)
        else:  # custom
            key = generate_custom_key(args.length)
        
        if args.format == 'env':
            print(f"ADMIN_SECRET_KEY={key}")
        else:
            print(key)
    
    print("\n💡 Usage Instructions:")
    print("1. Copy one of the generated keys above")
    print("2. Add it to Railway environment variables:")
    print("   - Go to Railway dashboard")
    print("   - Project Settings → Variables")
    print("   - Add: ADMIN_SECRET_KEY=your_generated_key")
    print("\n⚠️  Security Tips:")
    print("- Keep your secret key private")
    print("- Use different keys for different environments")
    print("- Regularly rotate your keys")
    print("- Never commit keys to version control")

if __name__ == "__main__":
    main() 