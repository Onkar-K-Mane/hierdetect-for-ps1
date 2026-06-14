import math
import re
import numpy as np

class LexicalFeatureExtractor:
    """Extracts 20 hand-crafted lexical features from PowerShell scripts."""

    @staticmethod
    def feat_length(s: str) -> float: 
        return float(len(s))
        
    @staticmethod
    def feat_entropy(s: str) -> float:
        if not s: 
            return 0.0
        freq = {c: s.count(c) / len(s) for c in set(s)}
        return float(-sum(p * math.log2(p) for p in freq.values() if p > 0))
        
    @staticmethod
    def feat_upper_ratio(s: str) -> float: 
        return sum(c.isupper() for c in s) / max(len(s), 1)
        
    @staticmethod
    def feat_digit_ratio(s: str) -> float: 
        return sum(c.isdigit() for c in s) / max(len(s), 1)
        
    @staticmethod
    def feat_space_ratio(s: str) -> float: 
        return s.count(' ') / max(len(s), 1)
        
    @staticmethod
    def feat_special_ratio(s: str) -> float: 
        return sum(not c.isalnum() and c != ' ' for c in s) / max(len(s), 1)
        
    @staticmethod
    def feat_pipe_count(s: str) -> float: 
        return float(s.count('|'))
        
    @staticmethod
    def feat_semicolon_count(s: str) -> float: 
        return float(s.count(';'))
        
    @staticmethod
    def feat_backtick_count(s: str) -> float: 
        return float(s.count('`'))
        
    @staticmethod
    def feat_paren_count(s: str) -> float: 
        return float(s.count('(') + s.count(')'))
        
    @staticmethod
    def feat_has_base64(s: str) -> float: 
        return float(bool(re.search(r'[A-Za-z0-9+/]{20,}={0,2}', s)))
        
    @staticmethod
    def feat_has_iex(s: str) -> float: 
        return float('iex' in s.lower() or 'invoke-expression' in s.lower())
        
    @staticmethod
    def feat_has_webclient(s: str) -> float: 
        return float('webclient' in s.lower() or 'downloadstring' in s.lower())
        
    @staticmethod
    def feat_has_enc(s: str) -> float: 
        return float(bool(re.search(r'-en[ce]\b', s, re.I)))
        
    @staticmethod
    def feat_has_bypass(s: str) -> float: 
        return float('bypass' in s.lower())
        
    @staticmethod
    def feat_has_hidden(s: str) -> float: 
        return float('hidden' in s.lower())
        
    @staticmethod
    def feat_has_nop(s: str) -> float: 
        return float(bool(re.search(r'-nop\b|-noprofile\b', s, re.I)))
        
    @staticmethod
    def feat_has_char_cast(s: str) -> float: 
        return float(bool(re.search(r'\[char\]', s, re.I)))
        
    @staticmethod
    def feat_has_convert(s: str) -> float: 
        return float(bool(re.search(r'\[convert\]', s, re.I)))
        
    @staticmethod
    def feat_unique_char_ratio(s: str) -> float: 
        return len(set(s)) / max(len(s), 1)

    FEATURE_FUNCS = [
        feat_length, feat_entropy, feat_upper_ratio, feat_digit_ratio,
        feat_space_ratio, feat_special_ratio, feat_pipe_count,
        feat_semicolon_count, feat_backtick_count, feat_paren_count,
        feat_has_base64, feat_has_iex, feat_has_webclient, feat_has_enc,
        feat_has_bypass, feat_has_hidden, feat_has_nop, feat_has_char_cast,
        feat_has_convert, feat_unique_char_ratio,
    ]

    @classmethod
    def extract(cls, script: str) -> np.ndarray:
        features = []
        for func in cls.FEATURE_FUNCS:
            try:
                features.append(func(script))
            except Exception:
                features.append(0.0)
        return np.array(features, dtype=np.float32)