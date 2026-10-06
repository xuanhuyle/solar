Status: discovery-grade: 2024-2025 French prices are public and already studied; 2025 is consumed (explorable, never confirmable). No result here counts as confirmed.

- t0 beats the best simple rule; the comparison with LEAR was not made (K1 failed or LEAR forecast too few days), so nothing is concluded about LEAR.
  - P1 (t0_cal vs best_simple_2023, MAE skill): state 'won'; pooled skill 0.227107; 95% interval [0.186116, 0.259087]; raw p 0.00049975; Holm p 0.001999; 2024 0.225383; 2025 0.228779; days 731
  - P2 (t0_cal vs lear_ens, MAE skill): state 'not runnable'; pooled skill not run; 95% interval not run; raw p not run; Holm p 1; 2024 not run; 2025 not run; days not run; cause: K1 failed
- t0's native bands score better than simple empirical bands, and its 10-90 band covers 70-90% of scored hours.
  - P3 (t0_cal vs best_simple_eq, pinball skill): state 'won'; pooled skill 0.251885; 95% interval [0.213317, 0.280905]; raw p 0.00049975; Holm p 0.001999; 2024 0.256492; 2025 0.247378; days 731; coverage 0.732786 (2024 0.722564, 2025 0.743037)
- Public weather forecasts issued before the gate add value to t0 on prices (P4 days only).
  - P4 (t0_cal_wx vs t0_cal, MAE skill): state 'won'; pooled skill 0.0284216; 95% interval [0.0114454, 0.0441206]; raw p 0.0009995; Holm p 0.001999; 2024 0.0151408; 2025 0.0367856; days 572
- P1 does not rest on t0 reading the D-1 afternoon prices.
  - t0_cal_strict vs best_simple_2023: pooled 0.067768, 2024 0.0809742, 2025 0.0549668; t0_cal_strict vs best_simple_2023_strict: pooled 0.153247, 2024 0.159079, 2025 0.147675

Day-ahead prices: Bundesnetzagentur | SMARD.de, CC BY 4.0, via Energy-Charts (Fraunhofer ISE)

Amended: A1 (2026-09-30, owner-approved) - the LEAR penalty is chosen as scikit-learn <= 0.23.1 chose it, as the published EPF forecasts were made (docs/experiment_4/AMENDMENTS.md). The frozen specification file and every threshold are unchanged; LEAR penalty step (1) is superseded by A1.
