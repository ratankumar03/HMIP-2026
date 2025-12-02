#!/usr/bin/env python
"""
Test script to display all registered URL patterns
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hmip_backend.settings')
django.setup()

from django.urls import get_resolver

def show_urls(urlpatterns, prefix=''):
    """Recursively show all URL patterns"""
    for pattern in urlpatterns:
        if hasattr(pattern, 'url_patterns'):
            # This is an include()
            show_urls(pattern.url_patterns, prefix + str(pattern.pattern))
        else:
            # This is a regular path
            if hasattr(pattern, 'name'):
                print(f"{prefix}{pattern.pattern}\t{pattern.name}")
            else:
                print(f"{prefix}{pattern.pattern}")

if __name__ == '__main__':
    resolver = get_resolver()
    print("Available URL patterns:")
    print("=" * 80)
    show_urls(resolver.url_patterns)
