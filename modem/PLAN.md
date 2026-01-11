# AFSK “Audio Modem” v0.1 (spec)

We're building a rudimental transmit/recieve program that uses audio to encode and transmit text. So basically, a primitive modem.

## Core parameters

* **Sample rate:** 48 000 Hz (TX+RX).
* **AFSK tones:** `mark=1200 Hz` (bit=1), `space=2200 Hz` (bit=0).
* **Symbol rates (baud):** 50, 100, 200, 400, 800.
  Rate codes: `0→50`, `1→100`, `2→200`, `3→400`, `4→800`.
* **Windows:** 2–5 ms raised-cosine ramps at symbol boundaries (avoid clicks).

## Start/End tones (fixed, single-kind)

* **Start tone:** 1000 Hz for **250 ms**.
* **End tone:** 1500 Hz for **250 ms**.
* Both are outside the data tones to simplify detection.

## Frame format (bitstream carried by AFSK)

```
[ START_TONE 250ms ]
[ PREAMBLE   0x55 repeated for ~200ms ]
[ SYNC WORD  0xDDAA ]
[ HEADER     5 bytes ]
[ PAYLOAD    N bytes (UTF-8 or ciphertext) ]
[ CRC-16     2 bytes (CCITT, poly 0x1021, init 0xFFFF, refin/refout=false) ]
[ END_TONE   250ms ]
```

### Header (5 bytes, byte-aligned)

* `V` (1 byte): protocol version (0x01).
* `R` (1 byte): rate code (0–4 as above).
* `F` (1 byte): flags bitfield

  * bit0: `ENC=1` if payload is encrypted (ChaCha20-Poly1305).
  * bit1: `FEC` (reserved, future).
  * others reserved (0).
* `LEN` (2 bytes, big-endian): payload length in bytes (not counting CRC).

### Preamble & sync

* **Preamble:** `0x55` (…0101…) repeated to ~200 ms at chosen baud (helps clock/threshold).
* **Sync word:** `0xDD, 0xAA`. Correlate on this to bit-align before reading header.

## Encoding (TX) outline

1. Build payload bytes (UTF-8 string; or ciphertext+tag if ENC=1).
2. Compose header (`V,R,F,LEN`), compute **CRC-16** over `[HEADER || PAYLOAD]`.
3. Serialize bits MSB-first.
4. Emit audio:

   * Start tone 1000 Hz 250 ms.
   * Preamble bits at chosen baud (alternate 0/1 so tones flip every symbol).
   * Sync word bits.
   * Header+payload+CRC bits.
   * End tone 1500 Hz 250 ms.
5. Apply short raised-cosine at each symbol transition. Play via `sounddevice`.

## Decoding (RX) outline

1. **Start detection:** Goertzel at 1000 Hz in sliding windows; when power>thresh for ~200–250 ms → “start”.
2. Switch to **AFSK band**:

   * Continuous Goertzel (or short FFT) at 1200/2200 Hz.
   * Make a soft or hard 0/1 decision each symbol period (start with fixed window; add fine alignment by maximizing mark/space contrast near expected centers).
3. **Preamble lock:** confirm alternating 0/1; refine clock.
4. **Sync detect:** correlate bit decisions against `0xDDAA` (16 bits). On peak → bit-align.
5. **Header:** read 5 bytes; derive baud from `R` (for *next* frame you can adapt sooner if you want), check `LEN`.
6. **Payload:** read `LEN` bytes; read **CRC-16** and verify; if fail → drop frame.
7. **Decrypt (if ENC=1):** ChaCha20-Poly1305 with pre-shared key; verify tag; output UTF-8 text.

## Variable speed

* TX picks a baud; encodes it into `R`. RX *starts* at a default (e.g., 200), but robustly finds preamble and sync anyway; after sync/header, it **knows** the sender’s baud and can adjust expectations (for next frames or mid-frame if you implement adaptive timing).

---

# Stretch goal: pre-shared key encryption (ChaCha20-Poly1305)

* **Key:** 32 bytes, read from a file (`--psk psk.hex` or raw).
* **Nonce (96-bit):** `nonce = concat( 32-bit unix_ts, 32-bit random, 32-bit counter )`. Include the 12-byte nonce **as the first 12 bytes of the payload** (plaintext).
  Then `ciphertext = AEAD_Encrypt(key, nonce, plaintext=msg_bytes, ad=HEADER)`. Append the 16-byte tag.
  Receiver reconstructs `nonce` from payload, uses same `HEADER` as associated data, verifies tag, and decrypts.
* **Payload when ENC=1:** `[ NONCE(12) || CIPHERTEXT || TAG(16) ]`, where `LEN` equals that total.

*(This gives integrity + confidentiality and binds header params to the ciphertext.)*

---

# CLI shape

* **Sender**

  ```
  $ send_text "Meet at the bridge at noon." --baud 400 --repeats 2 [--psk psk.bin]
  ```

  Options: `--rate-code` or `--baud`, `--repeats`, `--volume`, `--device`, `--wav-out out.wav`, `--no-end-tone` (debug).

* **Receiver**

  ```
  $ recv_text [--baud-default 200] [--psk psk.bin] [--device] [--wav-in file.wav]
  ```

  Prints: timestamp, detected baud, RSSI/SNR, CRC/AEAD status, and the message.

---

# Modules (minimal, testable)

```
modem/
  config.py        # tones, baud tables, sample rate, thresholds
  framing.py       # make_frame(), parse_header(), crc16()
  afsk.py          # bit->tone synth; Goertzel-based demod
  tx.py            # playback / WAV write
  rx.py            # mic capture, detectors, state machine
  crypto.py        # ChaCha20-Poly1305 wrappers, key loading
  utils.py         # windows, fades, byte<->bit, resampling
apps/
  send_text.py
  recv_text.py
tests/
  test_crc.py
  test_framing.py
  test_afsk_loopback.py
```

## Tooling & workflow

* Use [`uv`](https://docs.astral.sh/uv/) for Python env + dependency management.
* Initial setup: `uv sync` (installs deps, prepares virtual env).
* Local runs: `uv run apps/send_text.py ...`, `uv run apps/recv_text.py ...`.
* Add dev tooling (formatters, pytest) via `uv add --dev`.
* Run unit tests with `uv run pytest`.

---

# Practical defaults (good starting values)

* **Thresholds:** Start-tone detect when Goertzel power at 1000 Hz > (noise_floor + 12 dB) for ≥200 ms.
* **Preamble length:** ~200 ms worth of symbols at the chosen baud.
* **Symbol timing:** decide at center 60% of each symbol; allow ±5% drift before resync.
* **Buffers:** 20–40 ms audio blocks; double-buffered.

---

# Test plan (fast wins first)

1. **Unit tests:** cover `crc16`, header parsing/serialization, bit/byte helpers, windowing, and Goertzel routines.
2. **Pure loopback:** TX → WAV → RX on file; sweep SNR by adding AWGN; plot frame success vs SNR for each baud.
3. **Frequency offset:** detune tones ±30 Hz; confirm demod still clean.
4. **Room test:** laptop speakers→mic at 0.5–2 m; try 50/100 baud (“human-hearable”) and 400 baud.
5. **Encryption test:** flip `--psk` on/off; verify decrypt and tag failure on wrong key.
6. **Edge cases:** empty payload, max payload (e.g., 512–1024 bytes), CRC errors, truncated frames (no end tone).

---

# Unit test coverage goals

* `tests/test_crc.py`: validate CRC-16 against known vectors and incremental updates.
* `tests/test_framing.py`: ensure header pack/unpack round-trips, LEN limits enforced, CRC appended.
* `tests/test_afsk_loopback.py`: exercise bit-to-tone generation plus demod pipeline on short payloads at multiple baud rates.
* Add targeted tests for `utils.py` (bit <-> byte conversions, raised-cosine window generator) and `afsk.goertzel_power`.
* Aim for ≥90 % function coverage in `framing.py` and `afsk.py`, ≥80 % overall.

---

# Pseudocode snippets (reference)

**Goertzel power (single bin):**

```python
def goertzel_power(x, fs, f):
    N = len(x)
    k = int(0.5 + (N * f) / fs)
    w = 2 * np.pi * k / N
    coeff = 2 * np.cos(w)
    s0 = s1 = s2 = 0.0
    for n in x:
        s0 = n + coeff * s1 - s2
        s2, s1 = s1, s0
    return s1*s1 + s2*s2 - coeff*s1*s2
```

**Bit decision (per symbol window):**

```python
p_mark  = goertzel_power(window, 48000, 1200.0)
p_space = goertzel_power(window, 48000, 2200.0)
bit = 1 if p_mark > p_space else 0
```

**CRC-16-CCITT (common params):**

* poly `0x1021`, init `0xFFFF`, xorout `0x0000`, refin/refout `False`.

---

# Next concrete steps

1. Implement `framing.py` (header pack/unpack, CRC) + `afsk.py` (bit→tone synth; basic demod on arrays).
2. Write `tests/test_afsk_loopback.py` to prove: bytes → audio → bytes round-trip at 200 baud.
3. Add **start/end tone** detection + preamble/sync correlation in `rx.py`.
4. Wire up `send_text.py` and `recv_text.py`.
5. Add `--baud` switching and confirm the header’s rate code is honored.

If you want, I can scaffold the repo with these files and stubbed functions so you can fill in the guts.
