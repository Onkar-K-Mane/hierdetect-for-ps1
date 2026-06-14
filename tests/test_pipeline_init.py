import pytest
from pathlib import Path
from hierdetect.pipeline import HierarchicalDetector

def test_detector_initialization(mocker, tmp_path):
    """Test that the pipeline initializes and registers all 5 fusion strategies."""
    
    # Mock the heavy model loaders exactly where they are imported in pipeline.py
    mocker.patch('hierdetect.pipeline.TriageStage')
    mocker.patch('hierdetect.pipeline.TextBranch')
    mocker.patch('hierdetect.pipeline.GraphBranch')
    mocker.patch('hierdetect.pipeline.FusionLayer')

    # Create a fake thresholds file
    thresholds_file = tmp_path / "thresholds_per_seed.json"
    thresholds_file.write_text('{"triage_threshold": {"42": 0.35}}')

    detector = HierarchicalDetector(model_dir=tmp_path, seed=42)

    # Verify thresholds loaded correctly
    assert detector.triage_threshold == 0.35
    
    # Verify all 5 fusion strategies are mapped
    expected_strategies = ['averaging', 'stacking', 'cross_modal_attention', 'gated', 'moe']
    for strat in expected_strategies:
        assert strat in detector.fusions