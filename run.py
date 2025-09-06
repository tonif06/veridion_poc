#!/usr/bin/env python3
"""run.py
Main entrypoint for the POC.
This file simply delegates execution to `src/poc_entity_resolution.py`.
Usage:
    python run.py
"""
from src.poc_entity_resolution import main

if __name__ == "__main__":
    main()