# Learning Without a Reset

[Watch the lectures and use the interactive labs](https://gatech-rl2.github.io/reset-free-rl-explainers/)

Six original, narrated visual lectures on reset-free reinforcement learning. Each is **14 minutes**, with **12 chapters**, three equation steps per chapter, captions, a full transcript, and a working mathematical laboratory. The collection totals **84 minutes**, **72 chapters**, and **216 derivation steps**.

| Lesson | Topic | Primary sources |
| --- | --- | --- |
| 1. Foundations | Termination, truncation, controller handoffs, correct bootstrapping, and evaluation | [Time Limits in RL](https://proceedings.mlr.press/v80/pardo18a.html); [EARL](https://arxiv.org/abs/2112.09605) |
| 2. Leave no Trace | Learned recovery, action-conditioned aborts, ensembles, and limitations | [Eysenbach et al.](https://arxiv.org/abs/1711.06782) |
| 3. MEDAL | State-distribution matching, discriminator derivation, reset rewards, and Jensen–Shannon divergence | [Sharma et al.](https://arxiv.org/abs/2205.05212) |
| 4. RISC | Goal-conditioned bootstrapping, success critics, switching hazards, and survival probabilities | [Patil et al.](https://arxiv.org/abs/2405.01684) |
| 5. No-regret theory | Constrained MDPs, a shared saddle point, primal–dual regret, and sublinear expected resets | [Nguyen & Cheng](https://proceedings.mlr.press/v202/nguyen23b.html) |
| 6. MoReFree | World models, real back-and-forth exploration, imagined goal mixtures, and model error | [Yang et al., published version](https://arxiv.org/html/2408.09807v3) |

The presentation uses intuition, derivation, worked examples, and geometric animation, inspired by the user's references to Jia-Bin Huang's ML explanations and 3Blue1Brown's visual mathematics. The material and diagrams are original. Narration uses a neutral synthetic voice; this is an independent educational interpretation, not a work by those creators or the paper authors.

## Watch locally

Download or clone the repository and open `index.html`. Keep `assets`, `media`, `previews`, `captions`, and `transcripts` beside the HTML. Each lesson also has its own HTML entry point. Viewing and experiments need no installation, network connection, API key, or server.

For an optional localhost preview server with HTTP Range support for video seeking:

```sh
python3 serve.py --port 8769
```

Open `http://127.0.0.1:8769`. MP4s are H.264/AAC, 1600×900, 20 fps, with embedded chapter markers and selectable subtitle streams. Captions are also burned into the video.

## Laboratories and scope

The labs compute explicit teaching models. They are **not trained implementations or benchmark replications** of the papers.

- Foundations: exact one-state Bellman fixed points and a separate transition-target calculator.
- Leave no Trace: a declared discounted recovery model with biased ensemble estimates and threshold gates.
- MEDAL: normalized histograms, exact optimal discriminator, reset rewards, JS divergence, and an illustrative distribution-space update.
- RISC: exact finite-length switching distributions with a trajectory-level eligibility coin, minimum length, conservative factor, and maximum cutoff.
- No-regret theory: a two-policy known-payoff game plus explicitly schematic asymptotic curves. The theorem's feasibility and linear-MDP assumptions remain in the lecture.
- MoReFree: exact goal-mixture accounting and a constant-gain dynamics-error toy. An imagined rollout does not physically reset the environment.

Paper PDFs were consulted for research and are linked rather than redistributed. `sources/manifest.json` records the primary sources. Chapters distinguish paper claims from original illustrations.

## Rebuild

Use Python 3.12 and FFmpeg/FFprobe. Math assets and fonts are provided by Matplotlib. Narration regeneration needs an internet connection; the delivered videos do not.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/prepare_audio.py
.venv/bin/python src/prepare_math.py
.venv/bin/python src/render_all.py
.venv/bin/python src/render.py --previews
.venv/bin/python src/build_site.py
```

The content modules hold the original scripts. `content.json` contains aligned timings, captions, source notes, and equations. Browser tests use installed Google Chrome through Playwright; start the preview server before running `src/verify.py`. `src/verify_media.py` decodes every frame and audio stream and checks duration, chapter markers, subtitle timing, and narration levels. `src/package.py` creates a portable viewing-and-source archive.

GitHub Pages serves the repository's `main` branch at `/`; `.nojekyll` preserves the static site. There are no third-party scripts, analytics, or runtime external requests.

Related collection: [TAMP visual explainers](https://gatech-rl2.github.io/tamp-explainers/).
