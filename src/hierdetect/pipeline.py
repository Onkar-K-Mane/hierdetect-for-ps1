import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional
from hierdetect.models.triage import TriageStage
from hierdetect.models.text_branch import TextBranch
from hierdetect.models.graph_branch import GraphBranch
from hierdetect.models.fusion import FusionLayer

log = logging.getLogger('hierdetect.pipeline')

class HierarchicalDetector:
    """Full three-stage hierarchical detector orchestrating features and execution branches."""

    def __init__(self, model_dir: Path, seed: int = 42,
                 triage_threshold: float = 0.3,
                 codebert_max_len: int = 512,
                 codebert_stride: int = 128,
                 codebert_max_windows: int = 8,
                 gat_max_nodes: int = 800,
                 ast_timeout: int = 10):
        self.model_dir  = Path(model_dir)
        self.seed       = seed

        self.codebert_max_len     = codebert_max_len
        self.codebert_stride      = codebert_stride
        self.codebert_max_windows = codebert_max_windows
        self.gat_max_nodes        = gat_max_nodes
        self.ast_timeout          = ast_timeout

        self.triage_threshold = triage_threshold
        self.fusion_thresholds = {}
        self._load_thresholds(seed)

        log.info("─" * 60)
        log.info(f"  Loading models  (seed={seed})")
        log.info(f"  Triage escalation threshold : {self.triage_threshold:.4f}")
        log.info("─" * 60)

        # Stage 1 Initialization
        self.triage = TriageStage(
            self.model_dir / f'xgb_full_seed{seed}.json',
            self.model_dir / 'tfidf_vectorizer.pkl'
        )

        # Stage 2 Initialization
        self.text_branch  = TextBranch(
            self.model_dir / f'codebert_seed{seed}.pt',
            max_len=codebert_max_len,
            stride=codebert_stride,
            max_windows=codebert_max_windows,
        )
        self.graph_branch = GraphBranch(
            self.model_dir / f'gat_seed{seed}.pt',
            max_nodes=gat_max_nodes,
            ast_timeout=ast_timeout,
        )

        # Stage 3 Fusion Setup
        self.fusions = {}
        strategy_file_map = {
            'cross_modal_attention': 'attention',
            'gated':                 'gating',
            'moe':                   'moe',
            'stacking':              'stacking',
        }
        for strat in ['averaging', 'stacking', 'cross_modal_attention', 'gated', 'moe']:
            file_prefix = strategy_file_map.get(strat, strat)
            ext    = '.pkl' if strat == 'stacking' else '.pt'
            f_path = (self.model_dir / f'{file_prefix}_seed{seed}{ext}' if strat != 'averaging' else None)
            self.fusions[strat] = FusionLayer(strat, f_path)

    def _load_thresholds(self, seed: int):
        cfg_path = self.model_dir / 'thresholds_per_seed.json'
        if cfg_path.exists():
            try:
                with open(cfg_path) as f:
                    cfg = json.load(f)
                raw_triage = cfg.get('triage_threshold', {})
                if str(seed) in raw_triage:
                    self.triage_threshold = float(raw_triage[str(seed)])
                for strat in ['averaging', 'stacking', 'attention', 'gating', 'moe', 'cross_modal_attention']:
                    key = 'attention' if strat == 'cross_modal_attention' else strat
                    raw_strat = cfg.get(key, {})
                    if str(seed) in raw_strat:
                        self.fusion_thresholds[strat] = float(raw_strat[str(seed)])
            except Exception as e:
                log.warning(f"  Thresholds | could not parse {cfg_path.name}: {e}")

    def get_threshold(self, strategy: str, default: float = 0.5) -> float:
        return self.fusion_thresholds.get(strategy, default)

    def detect_script(self, script: str, full_pipeline: bool = False, strategy: str = 'all') -> Dict[str, Any]:
        result = {'timestamp': time.time(), 'script_length': len(script), 'seed': self.seed}

        try:
            triage_prob, _ = self.triage.predict_proba(script)
        except Exception:
            result['detection_stage'] = 'triage_error'
            result['final_malicious_prob'] = 0.5
            return result

        result['stage_1_malicious_prob'] = float(triage_prob)

        if not full_pipeline and triage_prob < self.triage_threshold:
            result['final_malicious_prob'] = float(triage_prob)
            result['detection_stage'] = 'triage_benign_fastpass'
            return result

        try: 
            text_prob = self.text_branch.predict_proba(script)
        except Exception: 
            text_prob = 0.5
        result['stage_2a_text_malicious_prob'] = float(text_prob)

        try: 
            graph_prob = self.graph_branch.predict_proba(script)
        except Exception: 
            graph_prob = 0.5
        result['stage_2b_graph_malicious_prob'] = float(graph_prob)

        fused_probs = {}
        strats_to_run = ['averaging', 'stacking', 'cross_modal_attention', 'gated', 'moe'] if strategy == 'all' else [strategy]

        for s in strats_to_run:
            fused_probs[s] = self.fusions[s].fuse(float(triage_prob), float(text_prob), float(graph_prob))
            
        result['stage_3_fused_probs'] = fused_probs
        primary = 'cross_modal_attention' if strategy == 'all' else strategy
        result['stage_3_fused_malicious_prob'] = fused_probs.get(primary, float(triage_prob))
        result['final_malicious_prob'] = result['stage_3_fused_malicious_prob']
        result['detection_stage'] = 'full_pipeline'
        
        return result