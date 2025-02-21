from .glassdoor import *
from .ifyoucould import *
from .linkedin import *
from .unjobs import *
from .workable import *
from .ziprecruiter import *
from .run_scrapers import run_scrapers  # ✅ Import run_scrapers here

JOB_SOURCES = ["glassdoor", "ifyoucould", "linkedin", "unjobs", "workable", "ziprecruiter"]

__all__ = ["fetch_glassdoor_jobs", "ifyoucould", "linkedin", "unjobs", "workable", "ziprecruiter", "run_scrapers"]