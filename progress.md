# Progress

- Started feasibility/design discovery. No implementation changes.
- Confirmed custom PyTorch Hub mixin path, no Transformers dependency, 4 GiB RTX 3050 GPU. Context7 Transformers docs did not index A-SINQ. Upstream API research delegated and still running. Asked user which checkpoint to target.
- Upstream review completed: HF Transformers rejects fresh A-SINQ; original A-SINQ calibrator is LLM/text-specific. User suggests tiny random checkpoint; need clarify whether test is Transformers-only or DA3-specific.
- Initialized project-root planning docs by moving the existing three planning files intact from `.planning/2026-09-27-0308-asinq-feasibility/`. User approved tiny random Transformers SINQ smoke test.
- Recorded Phase 3/4 task breakdown in task_plan.md. Chose cached qwen3_5 dummy fixture and the mlops quant-my-repo venv (sinq 0.2.0) for the smoke test; no repo changes yet.
- Session note: inference switched to z.ai (GLM-5.3) after openai-codex usage limit; work continues from recorded plan.
- Updated planning docs: worker-pool decision, quant-my-repo reuse directive, Phase 3/4 checklists expanded with worker subtasks and /tmp output paths.
- fixture-validate worker done: qwen3_5 fixture valid (8 files, 32 MB safetensors, 8.03M params), CPU dry-run + forward OK offline; cached HF-copy differs only in random weights. Report: /tmp/da3-fixture-report.json
- Smoke test attempt 5 PASSED (llama tiny, group 16, leaf-name exclusions). Persisted module+tests+script in quant-my-repo (TDD; 7/7 + 24/24; pyright clean). Phase 3 complete; awaiting sinq-api + da3-integration workers for Phase 4 report.
- sinq-api and da3-integration workers died in the provider-quota interrupt with no /tmp output; da3-integration findings salvaged from transcript (71 linears small; heads conv-only; per-preset subprocess enumeration) and respawned as da3-integration-v2 with constraints fn wired in. sinq-api dropped as superseded by empirical smoke evidence.
- quant-my-repo-map re-delivered and verified on disk after interrupt; key deltas: cached fixture keys miss under transformers 5.18.0.dev0, llmcompressor+spaces stubbing needed to import app.py, no runnable SINQ E2E exists in that repo yet. Note: its proposed qwen3_5 E2E would hit the sinq shape rules we proved (16-row k_proj fails) — a persistent E2E should use llama-tiny like our smoke script.
- sinq-api worker delivered post-interrupt: two SINQLinear classes; pip wheel sitecustomize auto-patches PreTrainedModel I/O (explains smoke round-trip; does NOT cover DA3 PyTorchModelHubMixin); SINQ_AUTO_PATCH=0 for isolation.
- da3-integration-v2 delivered complete Phase 4 sketch: GO; exclusions cam_dec.fc_t/fc_qvec/fc_fov.0 + cam_enc.pose_branch.fc1; lazy quantize after load; experiment ladder mono-large -> small -> bf16 shim. Presented Phase 4 report to user.
- Phase 4 GO presented; user approved ladder + commits + compaction prep. Key /tmp reports stashed to quant-my-repo/.planning/da3-sinq/ for durability.
- Commits: quant-my-repo 69ef576 (user dummy-gen renames, pre-staged) + 0e36e8b (da3_sinq module/tests/scripts); DA3 fork c992b78 (planning docs). Ladder step 1 da3mono-large parity launched (pid 5503), report -> /tmp/da3-parity-da3mono-large.json. Compaction prep: memory da3-sinq-phase4-design-state + docs + /tmp artifacts stashed in quant-my-repo/.planning/da3-sinq/.
- Ladder step 1 PASSED: da3mono-large 96/96 swapped, mean rel err 0.069%, p99 0.20%, Pearson 0.9928, fp32 CPU. Report stashed.
- quant-my-repo-map worker stored its asset map in-repo (docs/da3-quant-my-repo-map.md); committed separately.
