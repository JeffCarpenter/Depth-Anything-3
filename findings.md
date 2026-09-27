# Findings

## Requirements
- User wants quantization with Hugging Face `quantizers`, leaning toward A-SINQ.
- Target model, bitwidth, hardware and desired deliverable are not yet specified.

## Discoveries
- Pending inspection.

- Repository search: `DepthAnything3` inherits `PyTorchModelHubMixin`, rather than Transformers `PreTrainedModel`; inference uses `DepthAnything3.from_pretrained`.
- Worktree is initially dirty with user-owned `CLAUDE.local.md` and `basemind.toml`; no implementation changes made.

- `pyproject.toml` depends on `huggingface_hub` and PyTorch; it does not list `transformers` or `quantizers`.
- `DepthAnything3.forward` runs an autocast wrapper around a custom multi-view `DepthAnything3Net`; its inference path handles images, cameras, and export.
- Context7 returned no A-SINQ match in Transformers docs; investigating upstream quantizers separately.

## Upstream A-SINQ compatibility
- HF Transformers `SinqConfig(method="asinq")` is rejected for fresh quantization by `SinqHfQuantizer.validate_environment`; HF supports calibration-free `method="sinq"` under its model loading path. Source: https://github.com/huggingface/transformers/blob/96331a9f93b72697f160a958d2883d4b49a56739/src/transformers/quantizers/quantizer_sinq.py#L79-L87
- Original huawei-csl/SINQ A-SINQ expects tokenizer and text calibration, plus LLM anatomy (`layers`, `embed_tokens`, norm). DA3 does not meet this contract; no generic nn.Module whole-model A-SINQ API found. Source: https://github.com/huawei-csl/SINQ/blob/main/sinq/patch_model.py#L552-L624
- User suggested tiny random model as target; useful only for plumbing smoke test, not compression/accuracy validation of real DA3.
- Full upstream research is at `/tmp/da3-asinq-upstream.md`.

- User approved tiny random Transformers SINQ smoke test as first step, explicitly distinct from DA3/A-SINQ. HF test checkpoint `hf-internal-testing/tiny-random-LlamaForCausalLM` has ~1M parameters.

- Official Transformers docs list `SinqConfig(nbits=4, group_size=64, tiling_mode="1D", method="sinq")`, `AutoModelForCausalLM.from_pretrained(..., quantization_config=cfg, dtype=torch.bfloat16)`, and explicitly state A-SINQ is not supported by Transformers: https://github.com/huggingface/transformers/blob/main/docs/source/en/quantization/sinq.md

- User pointed to `~/code/mlops` and a Transformers fork. Existing `~/code/mlops/quant-my-repo/.planning/qwen3-5-awq-sinq-e2e-2026-08-25/` documents a prior tiny-random AWQ/SINQ end-to-end test. Inspect its code before building another smoke test.

- Existing mlops `quant-my-repo` has `quantize_sinq`, tests, and a generated `qwen3_5_dummy_models` checkpoint; follow that known setup to avoid needless model generation/dependency downloads. Prior notes warn `uv add` can trigger huge Torch downloads and recommend narrow `uv pip install --no-deps` in a venv with system site packages.
- User directive: leverage `~/code/mlops/quant-my-repo` heavily (venv with sinq 0.2.0 + gemlite, `quantize_sinq` in src/mlops/app.py, E2E notes in `.planning/qwen3-5-awq-sinq-e2e-2026-08-25/`, cached fixtures in `~/code/mlops/qwen3_5_dummy_models/` and `~/.cache/huggingface/awq-my-repo/`).
- Worker pool granted: up to 5 GLM-5.3 Flash agents, selector `zai/glm-5.3-flash`; GPU work stays serial on the single 4 GB RTX 3050.
- SINQ shape constraint (smoke attempt 1): `sinq/quantizer.py:rtn8` reshapes per-row scales to `(tile, -1)` where tile=32 for group_size=64; any weight with <32 output rows fails (qwen3_5 tiny k_proj=16, linear_attn in_proj=8). Tiny-model smoke needs group_size=8. Real DA3 linears (>=1024 dims) will not hit this.
- User directive: the DA3 SINQ integration module must live somewhere persistent (not /tmp); default proposal `src/depth_anything_3/quant/` in this repo, to confirm at Phase 4 gate.
## Smoke test result (Phase 3 complete)
- PASS after 5 attempts: hf-internal-testing/tiny-random-LlamaForCausalLM, nbits=4, group_size=16, tiling 1D, method=sinq, exclude lm_head+q/k/v/o_proj; cuda:0 via quant-my-repo venv.
- Evidence (/tmp/da3-sinq-smoke/report.json): 6 SINQLinear (both layers' MLP), 9 excluded Linears intact, forward finite (1,3,32000), save_pretrained/from_pretrained round-trip 6/6.
- SINQ shape rules (sinq 0.2.0): group_size multiple of 8 and >=16; group divides in_features; scale count = out_features*(in_features/group) must be multiple of 32 and >=32 (rtn8 tile=32 hard).
- modules_to_not_convert matches exact/prefix/regex-from-start/endswith — leaf names required.
- Persistent artifacts in quant-my-repo: src/mlops/da3_sinq.py (constraints fn, TDD 7/7), tests/test_da3_sinq.py, scripts/da3_sinq_smoke.py; pyright 0 errors; full suite 24/24 OK.
- quant-my-repo-map worker: no runnable SINQ E2E exists yet (phase 4 never started there); quantize_sinq at src/mlops/app.py:98-117; venv now resolves transformers 5.18.0.dev0 so old cache keys miss.
## sinq 0.2.0 API detail (sinq-api worker, /tmp/da3-sinq-api.md)
- Two SINQLinear classes: standalone `sinqlinear.py` (quantizes in __init__, used by AutoSINQHFModel.quantize_model) vs HF two-phase `sinqlinear_hf.py` (`quantize(weight, bias=None, layer_activations=None)`, state_dict={W_q,bias,meta}, `dequantize()`). Manual per-linear DA3 swaps should use the HF two-phase class.
- pip wheel ships `sitecustomize.py` that AUTO-PATCHES PreTrainedModel save/from/push every interpreter start (SINQ_AUTO_PATCH=0 disables) -> our smoke save/reload round-trip rode that patch; DA3 uses PyTorchModelHubMixin (not PreTrainedModel) so its autopatch DOES NOT apply — DA3 persistence needs `save_quantized_safetensors`/`from_quantized_safetensors` or custom state handling.
- `save_quantized_safetensors(model, tokenizer, save_dir, max_shard_size)` + `from_quantized_safetensors(save_dir, compute_dtype, device)` exist in pip 0.2.0.
- SinqConfig group_size%8 only warns in transformers; hard assert is in sinq_base_quant_config. CPU works (PyTorch backend, warning); gemlite needs 4-bit+1D+CUDA+in_f%group==0+in_f%32==0+dims>=16+axis1+meta.scale2.
- Set SINQ_AUTO_PATCH=0 in future smoke runs to isolate from autopatch behavior.
## DA3 linear inventory (da3-integration worker, raw: /tmp/da3-enum-results.json, /tmp/da3-linears-*.json)
- nn.Linear counts: small/base 71, large 119, mono/metric-large 96, giant 183 (backbone 160 + cam_dec 5 + cam_enc 18), nested 279. DPT/DualDPT/GSDPT heads and gs_adapter are conv-only: ZERO Linears. da3-base example: 135M total params, 118M in Linears (87%).
- Only 4 constraint violations per model (fail sinq rules): cam_dec fc_t/fc_qvec/fc_fov.0 (out<16, pose head) and cam_enc.pose_branch.fc1 (in=9). All backbone/cam_enc linears pass at group 64 incl. vitg xformers SwiGLU fused w12/w3.
- No SINQLinear.quantize in 0.2.0 standalone path: quantize happens in constructor; conversion = BasePatch.patch_linearlayers walk (named_modules, isinstance nn.Linear, setattr swap). quantize_model remains LLM-only.
- CRITICAL save constraint: nn.Module.state_dict() recursion skips SINQLinear overrides (returns {}); PyTorchModelHubMixin._save_pretrained saves params/buffers via safetensors save_model -> quantized weights invisible. Recommended pattern: keep dense hub checkpoint + lazy calibration-free quantize after .to(device).
- Risks flagged: bf16 autocast (api.py forward) vs gemlite dtype; FloatFunctional in dpt.py (leave untouched); DA3 does NOT use xformers attention (only fused SwiGLU FFN on vitg).
- Sketch: /tmp/da3-integration-sketch.md (sec 1 authoritative, 2-5 draft).
## Phase 4 verdict (da3-integration-v2, cross-checked vs sinq_layer_ok)
- GO for calibration-free SINQ on DA3. All backbone+trunk linears pass at group 64 AND 128; vitg fused SwiGLU included.
- Exclusion leaf names: cam_dec.fc_t, cam_dec.fc_qvec, cam_dec.fc_fov.0, cam_enc.pose_branch.fc1 (fc2 optional at group 128). Separate hard-assert gate vs gemlite N>=16 perf gate.
- Two SINQLinear variants confirmed: sinqlinear.py constructor-only vs sinqlinear_hf.py with .quantize(); replace_with_sinq_linear works on plain nn.Module but shells out weights; one-shot legacy swap recommended, keyword args mandatory.
- matmul has no dtype promotion: DA3's mixed autocast regions break a single compute_dtype; validate fp32 via direct net(x) first, then shim api.py.
- Experiment ladder: (1) da3mono-large 96 Linears zero exclusions plain Mlp, quantize-all one subprocess, fp32 forward parity vs baseline; (2) da3-small with exclusion list; (3) bf16-shimmed api.inference.
- Unknowns: vitg/xformers SwiGLU on CPU; gemlite+bf16 on CUDA (worker had no GPU — we have the RTX 3050 to test).
