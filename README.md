# StakedAssertion

**Stake GEN to make assertions.** Submit a claim with evidence URLs and a GEN stake. AI consensus verifies the claim. False claims get slashed.

Contract `0xdF702B05AbdD4A12B56F0C729b7F0dc48a416fdc` — StudioNet 61999

---

## How it works

```
submit_assertion(text, evidence_urls) + GEN stake
  ├─ leader: fetch evidence → AI verifies → verdict
  ├─ validator: fetch independently → AI verifies → must match
  └─ consensus: verdict + 4 checks → auto-slash if refuted
```

## The economics

| Verdict | Slash | Return |
|---------|-------|--------|
| CONFIRMED | 0% | 100% of stake |
| INCONCLUSIVE | 10% | 90% of stake |
| REFUTED | 50% | 50% of stake |

Slashed funds go to contract owner. Staker calls `withdraw_stake()` to reclaim remaining.

## Verification checks

| Check | Question |
|-------|----------|
| Accuracy | Does evidence support the factual claims? |
| Evidence | Sufficient evidence for a determination? |
| Consistency | Assertion consistent with evidence? |
| Completeness | Evidence covers all aspects? |

## Verdicts

- **CONFIRMED** — evidence supports the assertion
- **REFUTED** — evidence contradicts the assertion
- **INCONCLUSIVE** — evidence insufficient or ambiguous

## API

Write (payable):
- `submit_assertion(text, evidence_csv, context)` — must send GEN stake
- `withdraw_stake(assertion_id)` — reclaim remaining stake

View:
- `get_assertion(id)` / `get_verification(id)` / `get_stake(id)`
- `is_confirmed(id)` — boolean
- `get_stats()` / `get_version()`

## Validator comparison

Verdict + all 4 checks must match exactly. No tolerance.

## Use cases

- Fact-checking with economic incentives
- Dispute resolution with skin in the game
- Data verification with accountability
- Oracle attestation with slashing

## Tests

```
python -m pytest tests/test_stakedassertion.py -v
```
