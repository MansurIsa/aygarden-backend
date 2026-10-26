#!/usr/bin/env python
import os
import sys


def main():
    # Windows konsolunda Azərbaycan hərfləri üçün
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django tapılmadı. Virtual environment aktivdirmi və "
            "`pip install -r requirements.txt` icra olunubmu?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
