"""Reuse the previously measured profile-derived scheduling rule, unchanged."""
from pathlib import Path
import sys
ROOT=Path('/home/data3/txy')
C3=ROOT/'Documents/Codex/2026-09-21/cf_moa/effect_first_revision_20260923/cycle3'
sys.path[:0]=[str(ROOT),str(C3)]
from profile_derived_admission import admission
from cf_moa.evaluation import candidate_verify_runner
candidate_verify_runner.admission=admission
if __name__=='__main__': candidate_verify_runner.main()
