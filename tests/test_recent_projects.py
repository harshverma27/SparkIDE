import project.recent as recent


def _redirect(monkeypatch, tmp_path):
    store = tmp_path / "recent_projects.json"
    monkeypatch.setattr(recent, "recent_store_path", lambda: store)
    return store


def test_add_and_load_roundtrip(monkeypatch, tmp_path):
    _redirect(monkeypatch, tmp_path)
    a = tmp_path / "a"
    a.mkdir()
    recent.add_recent(a)
    assert recent.load_recent() == [a]


def test_add_is_mru_and_dedupes(monkeypatch, tmp_path):
    _redirect(monkeypatch, tmp_path)
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    recent.add_recent(a)
    recent.add_recent(b)
    recent.add_recent(a)  # bump a to front, no dupe
    assert recent.load_recent() == [a, b]


def test_load_prunes_missing(monkeypatch, tmp_path):
    store = _redirect(monkeypatch, tmp_path)
    gone = tmp_path / "gone"
    store.write_text(f'["{gone}"]')
    assert recent.load_recent() == []


def test_cap_at_ten(monkeypatch, tmp_path):
    _redirect(monkeypatch, tmp_path)
    for i in range(12):
        d = tmp_path / f"p{i}"
        d.mkdir()
        recent.add_recent(d)
    assert len(recent.load_recent()) == 10


def test_clear(monkeypatch, tmp_path):
    _redirect(monkeypatch, tmp_path)
    d = tmp_path / "a"
    d.mkdir()
    recent.add_recent(d)
    recent.clear_recent()
    assert recent.load_recent() == []
