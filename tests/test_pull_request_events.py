from tasks.silver.build_pull_request_events import _derive_events


def test_open_pr_generates_only_pr_opened_event():
    pr = {
        "number": 42,
        "title": "Add login page",
        "user": {"login": "alex"},
        "created_at": "2026-08-01T10:00:00Z",
        "merged_at": None,
        "closed_at": None,
    }

    events = _derive_events("alex/repo", pr)

    assert len(events) == 1
    assert events[0]["event_type"] == "pr_opened"
    assert events[0]["event_at"] == "2026-08-01T10:00:00Z"


def test_merged_pr_generates_opened_and_merged_events():
    pr = {
        "number": 43,
        "title": "Fix bug",
        "user": {"login": "alex"},
        "created_at": "2026-08-01T10:00:00Z",
        "merged_at": "2026-08-02T09:00:00Z",
        "closed_at": "2026-08-02T09:00:00Z",
    }

    events = _derive_events("alex/repo", pr)

    assert len(events) == 2
    event_types = {e["event_type"] for e in events}
    assert event_types == {"pr_opened", "pr_merged"}

    merged_event = next(e for e in events if e["event_type"] == "pr_merged")
    assert merged_event["event_at"] == "2026-08-02T09:00:00Z"


def test_closed_without_merge_generates_opened_and_closed_events():
    pr = {
        "number": 44,
        "title": "Abandoned feature",
        "user": {"login": "alex"},
        "created_at": "2026-08-01T10:00:00Z",
        "merged_at": None,
        "closed_at": "2026-08-03T15:00:00Z",
    }

    events = _derive_events("alex/repo", pr)

    assert len(events) == 2
    event_types = {e["event_type"] for e in events}
    assert event_types == {"pr_opened", "pr_closed"}


def test_merged_pr_never_generates_a_closed_event():
    pr = {
        "number": 45,
        "title": "Should not double-count",
        "user": {"login": "alex"},
        "created_at": "2026-08-01T10:00:00Z",
        "merged_at": "2026-08-02T09:00:00Z",
        "closed_at": "2026-08-02T09:00:00Z",
    }

    events = _derive_events("alex/repo", pr)

    event_types = [e["event_type"] for e in events]
    assert "pr_closed" not in event_types
    assert event_types.count("pr_merged") == 1