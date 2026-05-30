from django.urls import reverse


def _download_url(participation):
    return reverse("api_matchparticipation-download-match-log", kwargs={"pk": participation.id})


def test_download_match_log_without_file_returns_404(client, queued_match, user):
    """A queued match has no match_log yet. Requesting it should 404, not 500.

    Regression test: the new GraphQL API exposes participation IDs for matches that are
    scheduled but not yet played, so consumers request their (not-yet-existing) match logs.
    The endpoint used to raise ValueError("The 'match_log' attribute has no file associated
    with it.") and return a 500.
    """
    participation = queued_match.participant1  # bot owned by `user`
    client.force_login(user)

    response = client.get(_download_url(participation))

    assert response.status_code == 404


def test_download_match_log_without_permission_returns_404(client, queued_match, other_user):
    """A user who doesn't own the bot (and isn't staff) can't download the log."""
    participation = queued_match.participant1  # bot owned by `user`, not `other_user`
    client.force_login(other_user)

    response = client.get(_download_url(participation))

    assert response.status_code == 404
