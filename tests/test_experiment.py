from pathlib import Path
from errata.experiment import run

ROOT=Path(__file__).resolve().parents[1]

def test_local_stub_falsification_suite(tmp_path):
    r=run(tmp_path, ROOT/'fixtures/gtfs_static')
    assert r['change_id_same']
    assert r['revision_after_correction']==2
    assert r['hash_changed']
    assert r['interruption_zero_side_effect']
    assert not r['cumberland_final_skipped']
    assert r['king_edward_final_skipped']
    assert r['minimal_correction_pass']
    assert r['old_artifacts_stale']
    assert r['stale_commit_rejected']
    assert r['validator_pass']
    assert r['independent_consumer_version']=='2.0'
    assert not r['independent_consumer_cumberland_skipped']
    assert r['independent_consumer_king_edward_skipped']
    assert r['voice_text_convergence']
    assert r['negative_unknown_refused']
    assert r['boundary_conflict_raised']
    assert r['boundary_state_unchanged']
    assert r['duplicate_no_extra_revision']
    assert r['gtfs_rt_bytes'] > 0
