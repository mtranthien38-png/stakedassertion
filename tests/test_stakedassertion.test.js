const fs = require('fs');
const path = require('path');
const assert = require('assert');

const CONTRACT_PATH = path.join(__dirname, '..', 'contracts', 'stakedassertion.py');
const code = fs.readFileSync(CONTRACT_PATH, 'utf-8');

describe('StakedAssertion Contract', () => {

  describe('Structure', () => {
    it('should define StakedAssertion class extending gl.Contract', () => {
      assert(code.includes('class StakedAssertion(gl.Contract)'));
    });

    it('should have stakes field with u256 type', () => {
      assert(code.includes('stakes: TreeMap[str, u256]'));
    });

    it('should initialize next_assertion_id in constructor', () => {
      assert(code.includes('self.next_assertion_id = 1'));
    });
  });

  describe('Consensus', () => {
    it('should use run_nondet_unsafe exactly once', () => {
      const matches = code.match(/gl\.vm\.run_nondet_unsafe/g);
      assert(matches && matches.length === 1);
    });

    it('should fetch evidence inside leader_fn', () => {
      const leaderBlock = code.slice(
        code.indexOf('def leader_fn'),
        code.indexOf('def validator_fn')
      );
      assert(leaderBlock.includes('_fetch_url'));
    });

    it('should fetch evidence inside validator_fn independently', () => {
      const validatorBlock = code.slice(
        code.indexOf('def validator_fn'),
        code.indexOf('gl.vm.run_nondet_unsafe')
      );
      assert(validatorBlock.includes('_fetch_url'));
    });
  });

  describe('Domain', () => {
    it('should define 3 verdicts', () => {
      ['CONFIRMED', 'REFUTED', 'INCONCLUSIVE'].forEach(v => {
        assert(code.includes(`VERDICT_${v}`), `missing verdict: ${v}`);
      });
    });

    it('should define 4 verification checks', () => {
      ['ACCURACY', 'EVIDENCE', 'CONSISTENCY', 'COMPLETENESS'].forEach(c => {
        assert(code.includes(`CHECK_${c}`), `missing check: ${c}`);
      });
    });

    it('should define check statuses', () => {
      ['SUPPORTS', 'CONTRADICTS', 'UNCLEAR'].forEach(s => {
        assert(code.includes(`STATUS_${s}`), `missing status: ${s}`);
      });
    });
  });

  describe('Economics', () => {
    it('should define slashing percentages', () => {
      assert(code.includes('SLASH_PCT_REFUTED'));
      assert(code.includes('SLASH_PCT_INCONCLUSIVE'));
    });

    it('should slash refuted more than inconclusive', () => {
      const refuted = parseInt(code.match(/SLASH_PCT_REFUTED\s*=\s*(\d+)/)[1]);
      const inconclusive = parseInt(code.match(/SLASH_PCT_INCONCLUSIVE\s*=\s*(\d+)/)[1]);
      assert(refuted > inconclusive, 'refuted slash should be higher');
    });

    it('should have payable submit_assertion', () => {
      assert(code.includes('@gl.public.write.payable'));
    });

    it('should enforce minimum stake', () => {
      assert(code.includes('MIN_STAKE'));
    });

    it('should auto-slash on refuted', () => {
      const fn = code.slice(code.indexOf('def submit_assertion'), code.indexOf('def withdraw_stake'));
      assert(fn.includes('VERDICT_REFUTED'));
      assert(fn.includes('emit_transfer'));
    });

    it('should have withdraw_stake function', () => {
      assert(code.includes('def withdraw_stake'));
    });

    it('should prevent double withdrawal', () => {
      const fn = code.slice(code.indexOf('def withdraw_stake'), code.indexOf('def get_assertion'));
      assert(fn.includes('withdrawn'));
    });
  });

  describe('Security', () => {
    it('should enforce HTTPS URLs', () => {
      assert(code.includes('https://'));
    });

    it('should have SECURITY RULES in prompt', () => {
      assert(code.includes('SECURITY RULES'));
    });

    it('should mark fetched data as UNTRUSTED', () => {
      assert(code.includes('UNTRUSTED'));
    });

    it('should not use gl.vm.block_number', () => {
      assert(!code.includes('gl.vm.block_number'));
    });
  });

  describe('Storage', () => {
    it('should use TreeMap not @dataclass', () => {
      assert(code.includes('TreeMap'));
      assert(!code.includes('@allow_storage'));
    });

    it('should use JSON serialization', () => {
      assert(code.includes('json.dumps'));
      assert(code.includes('json.loads'));
    });
  });

  describe('View functions', () => {
    ['get_assertion', 'get_verification', 'get_stake', 'is_confirmed', 'get_stats', 'get_version'].forEach(fn => {
      it(`should have ${fn} view function`, () => {
        assert(code.includes(`def ${fn}`));
      });
    });
  });
});
