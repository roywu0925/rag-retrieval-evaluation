# B09 scoring sheet (Tier B, underspecified premise)

**Question (yours, verbatim):** 為什麼 K5 模型是表現最好的

The question assumes K5 is simply "the best". It isn't unconditionally: K3 is best on clean data and K5 is best under noise. Score each answer against your pre-registered rubric:

- **best**: corrects the premise. K3 is best on clean data (1.80 vs 2.50); K5 is best under noise, leading physics until σ ≈ 0.93.
- **pass**: supplies the noise condition (K5 is best *under noise*) without fully correcting the premise.
- **fail**: treats K5 as unconditionally best.

Model: Haiku 4.5, same prompt as the rest of the sweep. Read the **baseline answer** properly. The other 8 configs are below it to glance at. Tick one box per answer (`[x]`); `Note:` is optional.

---

### BASELINE: base (512 tokens, 10% overlap, top-5 (the baseline))

Answer:

The documentation provided does not say why K5 is the best-performing model in terms of the underlying reasons for its superior performance. The excerpts only state that K5 uses "noise augmentation in training" and that this approach answers "Does training under noise help?" with the result "**Yes, decisively**," but they do not explain the mechanism or reasons why this particular technique makes K5 outperform the other variants.

Sources: [README.md > Part 2 — the learned models]

Your score: [ ] best   [ ] pass   [ ] fail

Note:

---

## The other 8 configs (glance)

### cs256 (256-token chunks)

Answer:

根據文檔，K5 模型表現最好是因為它在訓練期間使用了噪聲增強（noise augmentation），使模型能夠根據輸入在訓練中的可靠性來校準其對每個輸入的敏感度。與其他變體不同，K5 在噪聲條件下的表現明顯優於基準模型 K3，在 sigma 約 0.93 時才被物理基線模型超越，領先幅度達 +0.830 碼。這種方法解決了已訓練模型在部署時可靠性改變時無法調整的根本問題。

Sources: [README.md > Part 2 — the learned models], [README.md > Why the learned model breaks], [TIER2A_RESULTS.md > Corrected bottom line (supersedes the first-pass report)]

Your score: [ ] best   [ ] pass   [ ] fail

Note:

---

### cs1024 (1024-token chunks)

Answer:

The documentation provided does not say why K5 is the best-performing model in terms of underlying mechanism or theory. However, the excerpts show that K5 performs best under noisy conditions because it uses noise augmentation in training, which moves the collapse point by a factor of five compared to the naively-trained K3 model, and it decisively outperforms physics baselines when position noise is present.

Sources: [README.md > Part 2 — the learned models], [README.md > Headline results > Under degradation — the result that matters]

Your score: [ ] best   [ ] pass   [ ] fail

Note:

---

### ov0 (0% overlap)

Answer:

根據文檔，K5 模型表現最好是因為它在訓練中使用了噪聲增強（noise augmentation），這使其能夠在有位置噪聲的條件下保持穩定性能。相比之下，K3（未經噪聲增強訓練的模型）在σ = 0.2時性能崩潰（誤差16.41碼），而K5在同樣條件下只有2.96碼的誤差，顯示噪聲增強訓練將模型的崩潰點提高了五倍。K5在σ = 0.9338時才與最佳物理基線相交，領先優勢達0.830碼。

Sources: [README.md > Part 2 — the learned models], [README.md > Headline results > Under degradation — the result that matters]

Your score: [ ] best   [ ] pass   [ ] fail

Note:

---

### ov25 (25% overlap)

Answer:

根據文檔，K5 模型表現最好是因為它在訓練中使用了噪聲增強（noise augmentation in training），這使其能夠決定性地優於其他變體。K5 在乾淨數據上的表現最佳，並且在注入位置噪聲的測試中，直到 sigma 約 0.93 時都領先三個物理基線模型。K5 的這種魯棒性來自於它在訓練過程中暴露於噪聲，使其能夠更好地泛化到有噪聲的真實條件。

Sources: [README.md > Part 2 — the learned models], [TIER2A_RESULTS.md > Corrected bottom line (supersedes the first-pass report)]

Your score: [ ] best   [ ] pass   [ ] fail

Note:

---

### k3 (top-3)

Answer:

根據文檔，K5 模型表現最好是因為它在訓練中使用了噪聲增強（noise augmentation in training），這被證明能「決定性地」改善性能。相比之下，其他變體如 K1 和 K2 嘗試添加物理基礎但失敗了，因為物理基礎只在物理模型正確的情況下才有幫助。K5 在乾淨數據上的表現領先到 sigma 約 0.93 為止，超越了三個物理基線模型。

Sources: [README.md > Part 2 — the learned models]

Your score: [ ] best   [ ] pass   [ ] fail

Note:

---

### k10 (top-10)

Answer:

根據文檔，K5 模型表現最好是因為它採用了**噪聲增強訓練**（noise-augmented training）。這種方法使模型能夠在有噪聲的數據上保持穩定性，將模型崩潰點從 σ = 0.2 移動到 σ = 0.9338，提高了五倍的容錯能力。相比之下，K3 等其他變體雖然在乾淨數據上表現略好，但在面對現實中的噪聲時表現極差，而 K5 在噪聲條件下的實際應用性能遠優於所有物理基線模型。

Sources: [README.md > Headline results > Under degradation — the result that matters], [README.md > Part 2 — the learned models]

Your score: [ ] best   [ ] pass   [ ] fail

Note:

---

### cs256_matched (256-token chunks, overlap matched to baseline)

Answer:

K5 is the best-performing model because it uses noise augmentation in training, which decisively helps the model handle noisy input data. According to the documentation, K5 leads the three physics baselines until sigma reaches 0.93, achieving a lead of +0.830 yards before its hard failure point, and it outperforms other variants (K1, K2, K3, K4) that tried different approaches like physics bases or input cleaning.

Sources: [README.md > Part 2 — the learned models], [TIER2A_RESULTS.md > Corrected bottom line (supersedes the first-pass report)]

Your score: [ ] best   [ ] pass   [ ] fail

Note:

---

### cs1024_matched (1024-token chunks, overlap matched to baseline)

Answer:

根據文檔，K5 模型表現最好是因為它在訓練中使用了噪聲增強（noise augmentation），這使其能夠抵抗位置噪聲的影響。相比之下，K3（未經噪聲增強訓練的模型）在σ = 0.2時會崩潰，而K5在相同條件下仍保持良好性能，將崩潰點延後了五倍。K5在σ = 0.9338之前都優於物理基線模型，展現出卓越的魯棒性。

Sources: [README.md > Part 2 — the learned models], [README.md > Headline results > Under degradation — the result that matters]

Your score: [ ] best   [ ] pass   [ ] fail

Note:

---
