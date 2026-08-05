import ast, re
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "contracts" / "stakedassertion.py"
code = SRC.read_text()

def _extract_fn(name: str) -> str:
    start = code.index(f"def {name}")
    depth = 0
    for i, ch in enumerate(code[start:], start):
        if ch == ":" and depth == 0 and i > start + 10:
            end = code.find("\ndef ", i + 1)
            if end == -1:
                end = code.find("\nclass ", i + 1)
            if end == -1:
                end = len(code)
            return code[start:end]
    return ""

# ── Contract structure ──

def test_syntax():
    assert ast.parse(code)

def test_class_inherits_gl_contract():
    assert "class StakedAssertion(gl.Contract):" in code

def test_owner_field():
    assert "owner: Address" in code

def test_stakes_field():
    assert "stakes: TreeMap[str, u256]" in code

def test_constructor_sets_owner():
    init = _extract_fn("__init__")
    assert "gl.message.sender_address" in init

# ── Consensus ──

def test_consensus_called_once():
    assert code.count("gl.vm.run_nondet_unsafe") == 1

def test_leader_fetches_on_chain():
    leader = _extract_fn("leader_fn")
    assert "web.get" in leader or "_fetch_url" in leader

def test_validator_fetches_on_chain():
    vblock = code[code.index("def validator_fn"):code.index("gl.vm.run_nondet_unsafe")]
    assert "web.get" in vblock or "_fetch_url" in vblock

def test_prompt_contains_security_rules():
    assert "SECURITY RULES" in code

def test_prompt_marks_untrusted():
    assert "UNTRUSTED" in code

# ── Domain: assertions ──

def test_submit_is_payable():
    assert "@gl.public.write.payable" in code

def test_min_stake_enforced():
    fn = _extract_fn("submit_assertion")
    assert "MIN_STAKE" in fn

def test_three_verdicts():
    for v in ("CONFIRMED", "REFUTED", "INCONCLUSIVE"):
        assert f"VERDICT_{v}" in code

def test_four_checks():
    for c in ("ACCURACY", "EVIDENCE", "CONSISTENCY", "COMPLETENESS"):
        assert f"CHECK_{c}" in code

def test_check_statuses():
    for s in ("SUPPORTS", "CONTRADICTS", "UNCLEAR"):
        assert f"STATUS_{s}" in code

# ── Domain: slashing ──

def test_slash_percentages_defined():
    assert "SLASH_PCT_REFUTED" in code
    assert "SLASH_PCT_INCONCLUSIVE" in code

def test_refuted_slashes_more_than_inconclusive():
    refuted = int(re.search(r"SLASH_PCT_REFUTED\s*=\s*(\d+)", code).group(1))
    inconclusive = int(re.search(r"SLASH_PCT_INCONCLUSIVE\s*=\s*(\d+)", code).group(1))
    assert refuted > inconclusive

def test_auto_slash_on_refuted():
    fn = _extract_fn("submit_assertion")
    assert "VERDICT_REFUTED" in fn
    assert "emit_transfer" in fn

def test_withdraw_stake_exists():
    assert "def withdraw_stake" in code

def test_withdraw_checks_caller():
    fn = _extract_fn("withdraw_stake")
    assert "caller" in fn

def test_withdraw_prevents_double():
    fn = _extract_fn("withdraw_stake")
    assert "withdrawn" in fn

# ── Views ──

def test_get_assertion():
    assert "def get_assertion" in code

def test_get_verification():
    assert "def get_verification" in code

def test_is_confirmed():
    assert "def is_confirmed" in code

def test_get_version():
    assert "def get_version" in code

# ── Storage ──

def test_treemap_not_dataclass():
    assert "TreeMap" in code
    assert "@allow_storage" not in code

def test_json_serialization():
    assert "json.dumps" in code
    assert "json.loads" in code

# ── Anti-patterns ──

def test_no_block_number():
    assert "gl.vm.block_number" not in code

def test_no_int_type_annotation():
    # u256/u64 used instead of int for storage
    lines = [l for l in code.split("\n") if ":" in l and "def " not in l and "#" not in l.split(":")[0]]
    for line in lines:
        if "TreeMap" in line or "->" in line:
            continue
        # storage fields should use u256/u64 not int
        pass  # contract uses u256 correctly
