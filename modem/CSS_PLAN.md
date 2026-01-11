CSS Modem (Chirp Spread Spectrum) — Detailed Implementation Plan

Goals
- Robust, room‑scale acoustic link (phone speaker → mic) that outperforms AFSK at low SNR and under multipath/AGC.
- Throughput on the order of 15–50 bps when configured for robustness with FEC.
- Integrate cleanly with existing framing (`modem.framing.Header`, CRC‑16) and CLIs.
- Provide unit tests with simulated channel impairments (noise, echoes, sample‑rate offset).

References/Approach
- CSS akin to LoRa: encode each symbol as a cyclic shift of a linear up‑chirp; demod by de‑chirp + FFT peak detection.
- Use real audio samples (float32) at `config.SAMPLE_RATE` (48 kHz). Multiply by complex reference chirp for de‑chirp; FFT on complex sequence.

Signal Specification (defaults)
- Sample rate: `fs = 48_000 Hz` (reuse `config.SAMPLE_RATE`).
- Acoustic band: center `fc = 2000 Hz` with bandwidth `BW = 1000 Hz` → sweep 1500–2500 Hz.
- Spreading factor: `SF = 8` → `M = 2^SF = 256` orthogonal cyclic shifts.
- Symbol duration: `Tsym = M / BW = 256 / 1000 = 0.256 s`.
- Samples per symbol: `Ns = round(fs * Tsym) ≈ 12_288` samples; keep as design variable computed from params.
- Preamble: 10 up‑chirps + 2 down‑chirps (for SFO estimation).
- Sync: 2 fixed data‑symbols (known cyclic shifts) after preamble for unambiguous lock and AFSK cross‑mode immunity.
- Mapping: Gray map bytes → 8‑bit symbol indices `0..255`; frame byte stream is segmented into symbols after FEC/interleaving.
- Windowing: raised‑cosine ramps of 2–3% per symbol to reduce click energy between symbols.
- Amplitude: normalize composite waveform to <= 0.8 peak (match AFSK path).

Core Math
- Up‑chirp instantaneous frequency: `f(t) = f0 + k t`, with `f0 = fc - BW/2`, `k = BW / Tsym`.
- Baseband complex chirp (analytic reference): `c(t) = exp(j 2π (f0 t + 0.5 k t^2))`.
- Passband real transmit signal for symbol with shift `m` (cyclic time shift): `s_m(t) = Re{ c((t + m*Tsym/M) mod Tsym) }`.
- Discrete time: `t[n] = n / fs`, `n = 0..Ns-1`.
- De‑chirp: multiply received window by `conj(c(t))` → ideally a single complex tone at bin index `m` (plus impairment terms).
- Detection: `FFT(dechirped)` magnitude → argmax bin `m_hat` in `0..M-1`.
- Optional zero‑padding by ×2 in FFT to sharpen peaks; use magnitude‑squared.

High‑Level Architecture
- New modules:
  - `modem/css.py`: parameters, chirp synthesis, symbol mapping, TX frame builder.
  - `modem/css_rx.py`: preamble/sync detection, SFO/CFO estimation, per‑symbol demod, confidence metrics, packet reassembly.
  - `modem/fec_conv.py`: convolutional encoder/soft‑decision Viterbi decoder (K=7, r=1/2).
- CLI apps:
  - `apps/send_text_css.py`: send text via CSS with options (SF, BW, repeats, fec, device, wav‑out).
  - `apps/recv_text_css.py`: receive via mic or wav; print decoded frames; `--open-channel` mode.
- Config updates:
  - Add CSS defaults (BW, FC, SF, preamble length) in `modem/config.py`.

Transmitter Design (modem/css.py)
1) Parameters/validation
   - Inputs: `sf`, `bw`, `fc`, `repeats`, `fec_enabled`, `interleave_depth` (optional).
   - Compute `M = 1 << sf`, `Tsym = M / bw`, `Ns = round(fs * Tsym)`.
   - Precompute reference complex chirp `c[n] = exp(j 2π (f0 n/fs + 0.5 k (n/fs)^2))` with `f0 = fc - bw/2`, `k = bw / Tsym`.
   - Precompute raised‑cosine window vector of length `Ns` with ramp fraction `0.02–0.03`.

2) Framing pipeline
   - Build `frame_core = Header || payload || CRC` via existing `framing.build_frame`.
   - If `fec_enabled`:
     - Convolutionally encode frame bits (rate 1/2, generators (133,171)_octal), producing `2x` bits.
     - Block interleave across symbols: choose `interleave_depth` (e.g., 4–8) and write/read columns.
   - Group coded bits into 8‑bit symbols (pad last symbol with zeros; carry pad length in header `flags` or as implicit known; simplest: no pad by requiring payload length%1=0 → always true since symbol=8 bits).
   - Apply Gray mapping `byte -> symbol_index (0..M-1)` (for SF=8 this is identity if we choose standard 8‑bit Gray code; include map/inverse helpers for generality).

3) Waveform construction
   - Preamble: concatenate `Npreamble` up‑chirps, then `Ndown=2` down‑chirps (use time‑reversed or negative‑slope chirp; for demod estimation only).
   - Sync: emit `Nsync=2` fixed symbol indices (e.g., 0x55, 0xAA) as cyclic shifts.
   - Data: for each symbol `m`, generate by cyclic time shift: `s_m[n] = Re{ c[(n + n_shift) mod Ns] } * window[n]`, where `n_shift = round(m * Ns / M)`.
   - Optional start/end tones for UX parity with AFSK (reuse `_sine_tone` from `tx.py`); make controlled by CLI flag.
   - Concatenate; scale to 0.8; return as `np.float32`.

Receiver Design (modem/css_rx.py)
1) Front‑end
   - Assume mono float32 input at fs=48 kHz.
   - Optional light band‑pass (1–3 kHz) via FIR/IIR; start with no filter to keep latency minimal.
   - Maintain rolling buffer for stream decoding similar to `IncrementalFrameDecoder` pattern.

2) Preamble detection
   - Sliding window of size `Ns`; step `Ns/8` (coarse) then refine.
   - For each candidate window:
     - Compute de‑chirped FFT magnitude peak power `P_peak` and total power `P_total`.
     - Accept if `P_peak/P_total > T_energy` and `P_peak` dominates neighborhood by `T_dom` (tune empirically; start with `T_energy≈0.1`, `T_dom≈8`).
   - On detection, refine start index forward to last window that still satisfies detection (captures trailing edge similar to AFSK logic).

3) SFO/CFO estimation (from preamble)
   - Using the `Ndown` down‑chirps, compute frequency/phase offset after de‑chirp. Estimate fractional bin offset `delta` per symbol (least squares over preamble peaks).
   - Maintain a running bin offset correction during data symbols by linearly extrapolating over time (accounts for small SFO).
   - Implementation: after de‑chirp, the ideal peak is at bin 0 for preamble up‑chirp. Estimate argmax bin and sub‑bin via quadratic interpolation near peak; compute drift per symbol.

4) Symbol timing
   - Lock symbol 0 start at refined preamble edge + `Npreamble*Ns`.
   - For each data symbol k:
     - Extract window `[k*Ns : (k+1)*Ns]`.
     - Multiply by `conj(c[n])` to de‑chirp (c[n] must be aligned without cyclic shift for data).
     - Compute `FFT` (size `Nfft = next_pow2(Ns)`; allow ×2 zero‑pad) and magnitude.
     - Apply fractional offset correction by circularly shifting the spectrum by `-delta_k` (or equivalently rotate samples before FFT).
     - Decide `m_hat = argmax(magnitude)` in `[0..M-1]`.
     - Confidence: `gamma = peak / max(second_peak, ε)` and `peak_energy = peak / total_energy`.

5) Byte/bitstream reconstruction
   - Map `m_hat` through inverse Gray to byte.
   - If `fec_enabled`: de‑interleave; Viterbi decode (soft or hard decisions). For soft metrics, map `gamma` or per‑bin LLR approximations into bit LLRs (start with hard decisions for simplicity; extend later).
   - Reassemble bytes into frame buffer; prepend header length guard.
   - Validate with `framing.parse_frame` (CRC) to accept.

6) Stream integration
   - Mirror the `IncrementalFrameDecoder` structure:
     - Buffer growth and search index management.
     - On partial detection, keep tail and continue.
     - Yield `(metadata, header, payload)` tuples with `timestamp`, `detected_params (sf,bw)`, `rssi` (RMS around preamble).

FEC and Interleaving (modem/fec_conv.py)
- Convolutional code: K=7, rate 1/2, polynomials (133, 171) in octal; tail‑biting or terminated (terminated initially).
- Encoder: straightforward shift register emit 2 bits per input bit.
- Decoder: Viterbi with path memory, traceback depth ≈ `5*(K-1) = 30` bits; start with hard decisions from symbol bytes.
- Interleaver: block interleave on bit stream to depth `D` (4–8). Pack/unpack utilities.
- Flagging: store FEC usage bit in `Header.flags` low bit (e.g., bit0 = 1 means FEC enabled).

Framing/Sync Choices
- Keep existing `Header` + CRC.
- Distinct sync from AFSK by:
  - Using CSS‑specific sync symbol pattern after preamble (e.g., `0x2D, 0xD4`).
  - Optionally omit legacy start/end tones unless `--tones` flag is set.
- Repeats: reuse `repeats` at CLI level to repeat entire frame N times for time diversity.

APIs (proposed)
- `modem.css`:
  - `ChirpParams(sf: int, bw: float, fc: float, fs: int)` dataclass with derived fields (`M, Tsym, Ns, k, f0`).
  - `generate_reference_chirp(params) -> np.ndarray complex64`.
  - `symbol_to_shift(symbol:int, params) -> int` and `shift_to_symbol(idx:int, params) -> int` (Gray mapping helpers).
  - `synthesize_symbols(symbols: Sequence[int], params, preamble=True, sync=True, tones=False) -> np.ndarray float32`.
  - `assemble_css_transmission(text: str, header: Header, params, repeats=1, fec=False, interleave=4) -> Iterable[float]`.
- `modem.css_rx`:
  - `CSSIncrementalDecoder(params, fec=False, interleave=4)` with `.ingest(samples)` yielding `(metadata, header, payload)`.
  - `detect_preamble(buffer) -> Optional[start_index]`.
  - `demod_symbol(window, params, sfo_state) -> (symbol:int, confidence:float)`.
- `modem.fec_conv`:
  - `conv_encode(bits: Iterable[int]) -> List[int]`.
  - `viterbi_decode_hard(bits: Iterable[int]) -> List[int]` (soft later).

CLIs
- `apps/send_text_css.py`
  - Args: `--sf 8`, `--bw 1000`, `--center 2000`, `--fec/--no-fec`, `--interleave 4`, `--repeats 1`, `--device`, `--wav-out`, `--tones/--no-tones`.
  - Constructs `Header` from message, assembles CSS waveform via `assemble_css_transmission`, plays or writes wav.
- `apps/recv_text_css.py`
  - Args: `--sf 8`, `--bw 1000`, `--center 2000`, `--fec/--no-fec`, `--interleave 4`, `--device`, `--wav-in`, `--open-channel`.
  - Uses `CSSIncrementalDecoder` to decode stream and prints frames.

Testing Plan (modem/tests)
1) Unit tests (fast)
   - `test_css_chirp_shapes`: correct `Ns`, continuity, amplitude bounds, windowing edges.
   - `test_css_dechirp_peak`: known symbol → de‑chirp + FFT argmax at expected bin.
   - `test_gray_mapping_roundtrip`: symbol ↔ byte roundtrip for all 256 values.
   - `test_conv_encoder_decoder`: random bits roundtrip with/without interleaving.

2) Loopback tests (moderate)
   - `test_css_loopback_basic`: encode random payload (32–64 bytes) → decode successfully with perfect channel.
   - `test_css_loopback_noise`: AWGN at various SNRs (e.g., 0–12 dB) and assert decode success above threshold.
   - `test_css_loopback_echo`: add delayed copy (e.g., 8 ms, −6 dB) to simulate room echo; expect success.
   - `test_css_sfo_tolerance`: resample RX by ±100 ppm equivalent; expect decode.

3) Streaming tests (slow/marked)
   - Incremental decoder on chunked buffers with pre/post junk audio; ensure single frame found.
   - Realistic AGC: apply amplitude ramps; expect stable detection (mark as `@pytest.mark.slow`).

Thresholds/Heuristics (initial)
- Preamble detection: `energy_ratio > 0.1`, `dominance > 8`. Tune with recordings.
- Symbol decision: accept if `gamma > 4` and `peak_energy > 0.05`; else mark as low‑confidence for soft decoding later.
- SFO correction: linear drift of up to ±200 ppm assumed; update per symbol.

Performance Considerations
- FFT length: `Nfft = 1 << ceil_log2(Ns)`; allow zero‑pad ×2 for clearer peaks with minimal CPU overhead.
- Avoid per‑call allocations: precreate chirp, window, FFT work buffers (use `rfft/irfft` if switching to real pipeline later).
- Streaming: keep search step coarse until a candidate is found; refine only locally to reduce CPU.

Risks/Unknowns
- Phone/mic DSP (AEC/NS/AGC) can distort chirps; recommend disabling in docs/CLI notes.
- Large multipath can create secondary peaks; `gamma` threshold and interleaving/FEC mitigate.
- Down‑chirp SFO estimation may be noisy on some devices; keep fallback to symbol‑by‑symbol fractional peak interpolation.

Milestones
1) TX MVP: chirp synth, symbol mapping, preamble/sync, frame assembly + CLI send (no FEC).
2) RX MVP: preamble detect, per‑symbol demod, basic sync; loopback decode in perfect channel.
3) Channel robustness: AWGN/echo tests; confidence metrics; threshold tuning.
4) FEC: add conv encoder/decoder, interleaver; update framing flag; tests with noise/echo.
5) Streaming: incremental decoder integrated with mic capture; open‑channel mode.
6) Docs/Examples: README section; sample commands; tuning tips.

Pseudocode Sketches
- Transmit (core):
  1. params = ChirpParams(sf, bw, fc, fs)
  2. frame = build_frame(header, payload)
  3. bits = bits_from_bytes(frame)
  4. if fec: bits = interleave(encode(bits))
  5. symbols = group_bits_into_bytes(bits)  # 0..255
  6. shifts = [gray_encode(b) for b in symbols]
  7. wav = [preamble_up, preamble_up, ..., down, down, sync1, sync2]
  8. for m in shifts: wav += synth_symbol(m)
  9. scale 0.8 → float32

- Receive (core):
  1. buffer += samples
  2. idx = find_preamble(buffer)  # sliding Ns window, dechirp+FFT energy test
  3. start = refine_edge(idx)
  4. k = estimate_sfo_from_downchirps()
  5. pos = start + Npreamble*Ns + Ndown*Ns + Nsync*Ns
  6. while pos + Ns <= len(buffer):
       window = buffer[pos:pos+Ns]
       z = window * conj(ref_chirp)
       X = FFT(z)
       m_hat = argmax(|X|)
       conf = peak_ratio(|X|)
       symbols.append(m_hat)
       pos += Ns
  7. bytes = [gray_decode(m) for m in symbols]
  8. if fec: bytes = decode(deinterleave(bytes_to_bits(bytes)))
  9. frame = parse_frame(bytes)
 10. yield (metadata, header, payload)

Integration Notes
- Keep CSS independent of AFSK paths; share only utilities (`utils`, `framing`, `tx.play_audio`, `tx.write_wav`).
- Add CSS choices to README with clear examples and caution to disable DSP on devices.
- Do not regress existing tests; CSS tests live alongside but isolated from AFSK ones.

Example CLI Commands (once implemented)
- `uv run apps/send_text_css.py "Hello CSS" --sf 8 --bw 1000 --center 2000 --fec --repeats 2 --wav-out css.wav`
- `uv run apps/recv_text_css.py --sf 8 --bw 1000 --center 2000 --open-channel`

Done Criteria
- CSS loopback tests pass (perfect, noisy, echo, ±100 ppm).
- Live decode across a room with phone at moderate volume for short payloads (<64 bytes) with FEC on.
- Documentation updated and CLIs usable with helpful `--help` text.

