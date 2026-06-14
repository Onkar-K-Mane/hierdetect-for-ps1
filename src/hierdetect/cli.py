import argparse
import json
import logging
import sys
from pathlib import Path
from hierdetect.pipeline import HierarchicalDetector

log = logging.getLogger('hierdetect.cli')

def print_detection_report(detector: HierarchicalDetector, res: dict, index: int, eval_strat: str, default_thresh: float):
    """Generates a highly readable, structured CLI report for a detection result."""
    stage = res.get('detection_stage', 'unknown')
    t1 = res.get('stage_1_malicious_prob', 0.0)

    print("\n" + "─"*70)
    print(f" DETECTION RESULT [{index}] ".center(70, "─"))
    print("─"*70)

    print(f" [Base Modalities]")
    print(f"  ├─ Stage 1 (XGBoost + Hand Features) : {t1:.4f}")

    if stage == 'triage_benign_fastpass':
        print(f"  ├─ Stage 2a (CodeBERT)               : SKIPPED (Fast-Passed)")
        print(f"  └─ Stage 2b (GATv2)                  : SKIPPED (Fast-Passed)\n")
        print(f" [Final Decision]")
        print(f"  * Verdict : ✅ BENIGN (Halted at Stage 1, Score: {t1:.4f} < {detector.triage_threshold:.4f})")
    
    elif stage == 'triage_error':
        print(f"  * Verdict : ⚠️ ERROR during Triage parsing")
    
    else:
        # Full Pipeline Executed
        t2a = res.get('stage_2a_text_malicious_prob', 0.5)
        t2b = res.get('stage_2b_graph_malicious_prob', 0.5)
        print(f"  ├─ Stage 2a (CodeBERT)               : {t2a:.4f}")
        print(f"  └─ Stage 2b (GATv2)                  : {t2b:.4f}\n")

        print(f" [Stage 3: Fusion Strategies]")
        fused_probs = res.get('stage_3_fused_probs', {})
        
        # Determine which strategies to display
        strats_to_show = fused_probs.items() if eval_strat == 'all' else [(eval_strat, fused_probs.get(eval_strat, 0.0))]

        for s, p in strats_to_show:
            strat_thresh = detector.get_threshold(s, default_thresh)
            is_malicious = p >= strat_thresh
            
            mark = '🚨' if is_malicious else '✅'
            cls = 'MALICIOUS' if is_malicious else 'BENIGN   '
            primary_tag = " (Primary)" if (eval_strat == 'all' and s == 'cross_modal_attention') else ""
            
            # Format: 🚨 MALICIOUS | Score: 0.8500 | Thresh: 0.5000 | Strategy: cross_modal_attention
            print(f"  {mark} {cls} │ Score: {p:.4f} (Thresh: {strat_thresh:.4f}) │ {s}{primary_tag}")

    print("─"*70)

def run_interactive(detector: HierarchicalDetector, default_threshold: float, force_full: bool = False):
    print("\n" + "═"*70)
    print(" HIERDETECT INTERACTIVE REPL MODE ".center(70, "═"))
    print("═"*70)
    print(f"Stage 1 Triage Threshold : {detector.triage_threshold:.4f}")
    print(f"Force Full Pipeline (-F) : {'ON (No Fast-Pass)' if force_full else 'OFF (Standard Fast-Pass)'}")
    print("Press Ctrl+C at any time to exit.\n")

    strat_map = {'1': 'averaging', '2': 'stacking', '3': 'cross_modal_attention', '4': 'gated', '5': 'moe', '6': 'all'}
    
    while True:
        try:
            print("\nSelect Fusion Strategy:")
            for k, v in strat_map.items():
                print(f"  [{k}] {v.replace('_', ' ').title() if v != 'all' else 'ALL Strategies'}")
            print("  [0] Exit")
            
            choice = input("\nEnter choice (0-6) [default: 6]: ").strip()
            if choice == '0': 
                break
            strategy = strat_map.get(choice or '6')
            if not strategy: 
                continue
                
            target = input("\nEnter script path OR raw command: ").strip().strip("\"'")
            if not target: 
                continue
            
            if Path(target).is_file():
                with open(target, 'r', encoding='utf-8', errors='ignore') as f: 
                    script = f.read()
            else:
                script = target
                
            res = detector.detect_script(script, full_pipeline=force_full, strategy=strategy)
            print_detection_report(detector, res, 1, strategy, default_threshold)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            log.error(f"Error processing input: {e}")

def run_self_check(detector) -> bool:
    b_sample = "Write-Host 'Hello World'"
    m_sample = "powershell.exe -EncodedCommand JABjACAAPQAgAE4AZQB3AC0ATwBiAGoA"
    
    b_res = detector.detect_script(b_sample, full_pipeline=False)
    m_res = detector.detect_script(m_sample, full_pipeline=False)
    
    log.info(f"Self Check Done. Benign Score: {b_res['final_malicious_prob']:.4f} | Malicious Score: {m_res['final_malicious_prob']:.4f}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Hierarchical PowerShell Detection CLI Entrypoint')
    parser.add_argument('--model-dir', type=Path, required=True, help="Path to models directory")
    parser.add_argument('--seed', type=int, default=42, choices=[42, 1337, 2024], help="Random seed for model selection")
    parser.add_argument('--fusion-strategy', type=str, default='all', choices=['all', 'averaging', 'stacking', 'cross_modal_attention', 'gated', 'moe'])
    parser.add_argument('--triage-threshold', type=float, default=0.3, help="Stage 1 escalation threshold")
    parser.add_argument('--threshold', type=float, default=0.5, help="Fallback malicious classification threshold")
    
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument('--script', type=Path, help="Path to PowerShell script file")
    input_group.add_argument('--command', type=str, help="Raw command string")
    input_group.add_argument('--batch', type=Path, help="Text file with one script/command per line")
    
    parser.add_argument('-F', '--full-pipeline', action='store_true', default=False, help="Force all 3 stages (bypass fast-pass)")
    parser.add_argument('--interactive', action='store_true', help="Start REPL mode")
    parser.add_argument('--output', type=Path, help="Save JSON output to path")
    parser.add_argument('--check', action='store_true', help="Run internal sanity check")

    args = parser.parse_args()

    detector = HierarchicalDetector(
        model_dir=args.model_dir, 
        seed=args.seed, 
        triage_threshold=args.triage_threshold
    )

    if args.check:
        sys.exit(0 if run_self_check(detector) else 1)

    if args.interactive or not any([args.script, args.command, args.batch]):
        run_interactive(detector, args.threshold, args.full_pipeline)
        sys.exit(0)

    # Standard Execution
    results = []
    if args.script:
        with open(args.script, 'r', encoding='utf-8', errors='ignore') as f:
            results.append(detector.detect_script(f.read(), full_pipeline=args.full_pipeline, strategy=args.fusion_strategy))
    elif args.command:
        results.append(detector.detect_script(args.command, full_pipeline=args.full_pipeline, strategy=args.fusion_strategy))
    elif args.batch:
        with open(args.batch, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        for line in lines:
            results.append(detector.detect_script(line, full_pipeline=args.full_pipeline, strategy=args.fusion_strategy))

    # Print UX Report
    for i, res in enumerate(results, 1):
        print_detection_report(detector, res, i, args.fusion_strategy, args.threshold)

    # Save JSON if requested
    if args.output:
        with open(args.output, 'w') as f: 
            json.dump(results, f, indent=2)
        log.info(f"JSON results saved to {args.output}")

if __name__ == '__main__':
    main()