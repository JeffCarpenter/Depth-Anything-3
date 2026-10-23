# Task Plan: Hugging Face quantizers for Depth Anything 3

## Goal
Validate the approved tiny random Transformers SINQ smoke test; record the limits of applying it to DA3 and A-SINQ.

## Next Step
Step 1 PASSED (96/96 swapped, r=0.993, mean rel err 0.069%). Next: step 2 da3-small with exclusion list, then step 3 bf16 shim.

## Current Phase
Phase 3

## Phases
### Phase 1: Discover repository loading and quantizer support
- **Status:** complete
### Phase 2: Present design and clarify target artifact
- **Status:** complete
### Phase 3: Disposable Transformers smoke test and verification
- **Status:** complete
- [x] Worker `sinq-api` (delivered late after quota interrupt: /tmp/da3-sinq-api.md; two-phase SINQLinear + sitecustomize autopatch facts recorded): introspect sinq 0.2.0 API in quant-my-repo venv (SinqConfig fields, `SINQLinear.quantize` signature, save/reload helpers, device rules) -> /tmp/da3-sinq-api.md
- [x] Worker `fixture-validate`: validate cached qwen3_5 dummy fixture (config, safetensors, CPU-only `from_pretrained` dry run via venv) -> /tmp/da3-fixture-report.json
- [x] Worker `quant-my-repo-map`: catalog reusable quant-my-repo assets (`quantize_sinq`, E2E patterns, cached fixtures incl. `~/.cache/huggingface/awq-my-repo/`, pitfalls) -> /tmp/da3-quant-my-repo-map.md
- [x] Write smoke script (persistent copy: quant-my-repo/scripts/da3_sinq_smoke.py): load cached `Qwen3_5ForConditionalGeneration` with `SinqConfig(nbits=4, group_size=64, tiling_mode="1D", method="sinq", modules_to_not_convert=["lm_head"])`, cuda:0, via `/home/jeff/code/mlops/quant-my-repo/.venv/bin/python`
- [x] Evidence: 6 SINQLinear (MLP), 9 Linears excluded, forward finite, save/reload OK -> /tmp/da3-sinq-smoke/report.json
- [x] Round-trip: save_pretrained + from_pretrained, 6/6 SINQ modules reloaded
- [x] Evidence recorded; Phase 3 complete
- **Status:** in_progress
### Phase 4: Report results and DA3 integration options
- [x] Worker `da3-integration-v2`: classification confirmed at group 64/128; GO verdict; experiment ladder defined -> /tmp/da3-integration-sketch.md complete
- [ ] Summarize smoke-test outcome to user
- [ ] Present DA3 options: (a) custom per-linear calibration-free SINQ replacement on `DepthAnything3Net` via `SINQLinear.quantize`, (b) original-repo A-SINQ (blocked: tokenizer/text calibration + LLM anatomy), (c) no off-the-shelf A-SINQ path without a custom vision-calibration adapter
- [ ] Await user decision before any repo code change
- **Status:** pending

## Key Questions
- Which model/checkpoint, hardware, output format, and target bits?
- Does A-SINQ support this custom nn.Module without Transformers integration?

## Decisions Made
| Decision | Rationale |
|---|---|
| Tiny Transformers SINQ smoke test first | Approved by user; this tests the HF path without claiming DA3 or A-SINQ support. |
| Discovery before implementation | Avoid inventing unsupported API or changing model behavior without user approval. |
| Run smoke test through `~/code/mlops/quant-my-repo/.venv` | That venv already has `sinq==0.2.0` + gemlite on CUDA; avoids installs here, matches prior E2E notes warning against broad `uv add`. |
| Keep smoke artifacts in /tmp | Throwaway plumbing test; this repo stays untouched until Phase 4 decision. |
| Worker pool: up to 5 GLM-5.3 Flash (`zai/glm-5.3-flash`) | User-granted; parallel research workers, serial GPU work stays inline. |
| Leverage quant-my-repo heavily | User directive: reuse its venv (sinq 0.2.0), `quantize_sinq`, E2E patterns, cached fixtures, and prior planning notes instead of rebuilding. |
| DA3 SINQ module persists in quant-my-repo | User directive (stated twice): `src/mlops/da3_sinq.py` + `tests/test_da3_sinq.py` + `scripts/da3_sinq_smoke.py`, TDD-built; enables mcpls/pyright leverage on real code. |

## Errors Encountered
| Error | Attempt | Resolution |
|---|---|---|
| Python environment probe NameError from shell quoting | 1 | Re-ran with Python shlex.quote; dependencies detected. |
| SyntaxError in filename-list Python comprehension | 1 | Split expression into named intermediate `files`; subsequent read succeeded. |
| `find_models('GLM-5.3 Flash z.ai glm flash')` returned [] | 1 | Broadened query to 'glm'; found selector `zai/glm-5.3-flash`. |
| SINQ smoke attempt 1: `RuntimeError: shape '[32,-1]' invalid` in `sinq/quantizer.py:rtn8` on qwen3_5 k_proj (16 rows) and linear_attn in_proj (8 rows) | 1 | group_size=64 implies tile=32; tiny fixture has <32-row linears. Attempt 2: group_size=8 (tile fits all tiny dims). |
| Attempt 2 (qwen3_5, group 8): `dual_shift.py` asserts block>=16 and must divide input dim; qwen3_5 has 37-dim layers | 2 | Switched fixture to llama tiny (clean 16/64 dims). |
| Attempt 3 (llama tiny, group 16): rtn8 tile is hardcoded 32; 16x16 attn projections yield only 16 scales | 3 | Attempt 4: keep group 16, exclude `self_attn` + `lm_head`; MLP linears (64x16, 16x64) satisfy >=32 scales. Full plumbing still exercised. |
