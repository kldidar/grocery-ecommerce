from apps.common.tasks import ping


def test_ping_task_executes_through_delay() -> None:

    result = ping.delay()
    assert result.get() == "pong"
