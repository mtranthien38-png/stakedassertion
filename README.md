# stakedassertion

Stake GEN to make on-chain assertions. Get slashed if wrong.

## contract

```
0xdF702B05AbdD4A12B56F0C729b7F0dc48a416fdc  (StudioNet 61999)
```

## the idea

Anyone can assert a fact on-chain. But assertions cost GEN.
If the assertion is **confirmed** by AI consensus → full stake returned.
If **refuted** → 50% slashed.
If **inconclusive** → 10% slashed.

This creates economic incentives for truthful assertions.

## example flow

```python
# assert with 1 GEN stake
aid = submit_assertion(
    "Bitcoin reached $100k on Dec 5 2024",
    "https://en.wikipedia.org/wiki/Bitcoin,https://coingecko.com/en/coins/bitcoin",
    context="Historical price verification"
)  # value=1000000000000000000

# check result
is_confirmed(aid)  # → True if evidence supports

# withdraw remaining stake
withdraw_stake(aid)
```

## slashing table

| verdict | slash | you get back |
|---------|-------|-------------|
| CONFIRMED | 0% | 100% |
| INCONCLUSIVE | 10% | 90% |
| REFUTED | 50% | 50% |

Slashed funds go to contract owner via `emit_transfer`.

## consensus

```
submit_assertion(text, evidence_urls) + GEN
│
├─ leader_fn()
│   └─ fetch all evidence → AI verifies accuracy/evidence/consistency/completeness
│
├─ validator_fn()
│   └─ fetch independently → AI verifies → must match leader
│
├─ if REFUTED: auto-slash 50% to owner
├─ if INCONCLUSIVE: auto-slash 10% to owner
└─ result stored on-chain
```

## verification checks

| check | question |
|-------|----------|
| accuracy | evidence supports factual claims? |
| evidence | sufficient for determination? |
| consistency | assertion consistent with evidence? |
| completeness | evidence covers all aspects? |

## verdicts

| verdict | meaning |
|---------|---------|
| CONFIRMED | evidence supports assertion |
| REFUTED | evidence contradicts assertion |
| INCONCLUSIVE | evidence insufficient |

## validator comparison

```python
if my["verdict"] != leader["verdict"]:   return False
if my["checks"] != leader["checks"]:     return False
return True
```

Exact match on verdict + all 4 checks. No tolerance.

## API

### write (payable)

| function | params | value | returns |
|----------|--------|-------|---------|
| `submit_assertion` | text, evidence_csv, context? | GEN stake | assertion_id |
| `withdraw_stake` | assertion_id | — | — |

### view

| function | returns |
|----------|---------|
| `get_assertion(id)` | full assertion JSON |
| `get_verification(id)` | verdict + checks |
| `get_stake(id)` | staked amount |
| `is_confirmed(id)` | bool |
| `get_stats()` | {owner, total_assertions} |
| `get_version()` | "stakedassertion/1.0.0" |

## tests

```bash
npm test
# 29 Python + 28 JavaScript
```

## tech

- `gl.vm.run_nondet_unsafe` — leader-validator consensus
- `gl.nondet.web.get` — on-chain fetch (inside consensus)
- `gl.nondet.exec_prompt` — AI verification
- `gl.public.write.payable` — staked submissions
- `emit_transfer` — slashing payouts
- `TreeMap[str, str]` + `TreeMap[str, u256]` — storage
- No `@dataclass`, no `gl.vm.block_number`
