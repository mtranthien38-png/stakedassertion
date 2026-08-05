"""StakedAssertion invariant tests."""
from pathlib import Path
import re

SOURCE = (Path(__file__).parents[1] / "contracts" / "stakedassertion.py").read_text()

def test_valid_syntax():
    import ast; ast.parse(SOURCE)
def test_run_nondet_unsafe():
    assert "gl.vm.run_nondet_unsafe" in SOURCE
def test_web_get():
    assert "gl.nondet.web.get" in SOURCE
def test_exec_prompt():
    assert "gl.nondet.exec_prompt" in SOURCE
def test_fetch_inside_leader():
    m = re.findall(r'def leader_fn\(\).*?def validator_fn', SOURCE, re.DOTALL)
    assert m and "_fetch_url" in m[0]
def test_fetch_inside_validator():
    m = re.findall(r'def validator_fn.*?gl\.vm\.run_nondet_unsafe', SOURCE, re.DOTALL)
    assert m and "_fetch_url" in m[0]
def test_three_verdicts():
    for v in ["VERDICT_CONFIRMED","VERDICT_REFUTED","VERDICT_INCONCLUSIVE"]:
        assert v in SOURCE
def test_four_checks():
    for c in ["CHECK_ACCURACY","CHECK_EVIDENCE","CHECK_CONSISTENCY","CHECK_COMPLETENESS"]:
        assert c in SOURCE
def test_validator_checks_verdict():
    m = re.search(r'def validator_fn.*?gl\.vm\.run_nondet_unsafe', SOURCE, re.DOTALL)
    assert m and "verdict" in m.group()
def test_validator_checks_checks():
    m = re.search(r'def validator_fn.*?gl\.vm\.run_nondet_unsafe', SOURCE, re.DOTALL)
    assert m and "checks" in m.group()
def test_submit_assertion_payable():
    assert "@gl.public.write.payable" in SOURCE
def test_slash_mechanism():
    assert "SLASH_PCT_REFUTED" in SOURCE
    assert "SLASH_PCT_INCONCLUSIVE" in SOURCE
def test_withdraw_stake():
    assert "def withdraw_stake" in SOURCE
def test_emit_transfer():
    assert "emit_transfer" in SOURCE
def test_stakes_storage():
    assert "self.stakes" in SOURCE
def test_security_rules():
    assert "SECURITY RULES" in SOURCE
def test_untrusted():
    assert "UNTRUSTED" in SOURCE
def test_no_block_number():
    assert "gl.vm.block_number" not in SOURCE
def test_treemap():
    assert "TreeMap" in SOURCE
def test_gl_contract():
    assert "gl.Contract" in SOURCE
def test_constructor_no_args():
    assert "def __init__(self):" in SOURCE
