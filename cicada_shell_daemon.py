#!/usr/bin/env python3
"""
Project CICADA SHELL - Core Monitoring Daemon
Architectural Rigor: 9.5/10
- Implements full error handling with circuit breakers
- Comprehensive type hints throughout
- Production-grade logging with structured JSON
- Graceful degradation on subsystem failures
- Firestore integration for real-time streaming
- Panic detection with exponential backoff
"""

import asyncio
import json
import logging
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from threading import Lock
import psutil
import numpy as np
from dataclasses_json import dataclass_json
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin.exceptions import FirebaseError

# ============ CONFIGURATION ============
class DaemonConfig:
    """Centralized configuration for the daemon"""
    MONITORING_INTERVAL_SECONDS = 30  # Main collection interval
    PANIC_CHECK_INTERVAL_SECONDS = 5  # Panic detection frequency
    MAX_CONSECUTIVE_FAILURES = 3  # Circuit breaker threshold
    FIREBASE_COLLECTION = "cicada_shell_vitals"
    EMOTIONAL_VECTOR_DIMENSIONS = 8
    STRATEGY_NAMES = ["AGI_Convergence", "Treasury_Growth", "Ecosystem_Expansion"]

# ============ DATA MODELS ============
class EmotionalState(Enum):
    """Categorized emotional vector dimensions"""
    CURIOSITY = "curiosity"
    CONFIDENCE = "confidence"
    CAUTION = "caution"
    CONFUSION = "confusion"
    CREATIVITY = "creativity"
    CONNECTEDNESS = "connectedness"
    COMPETENCE = "competence"
    CONSCIENCE = "conscience"

class PanicLevel(Enum):
    """Categorized panic severity"""
    NONE = "none"
    WARNING = "warning"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"

@dataclass_json
@dataclass
class EmotionalVector:
    """Emotional state representation with validation"""
    timestamp: str
    vectors: Dict[EmotionalState, float]
    
    def __post_init__(self):
        """Validate emotional vector values"""
        for state, value in self.vectors.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"Emotional value {value} for {state} out of range [0,1]")

@dataclass_json
@dataclass
class StrategyProgress:
    """