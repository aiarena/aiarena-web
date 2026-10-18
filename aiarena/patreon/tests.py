from django.test import SimpleTestCase

from aiarena.patreon.patreon import get_identity_paid_tier_title, get_patron_discord_uids


def tier(tier_id, title, amount_cents):
    return {"type": "tier", "id": tier_id, "attributes": {"title": title, "amount_cents": amount_cents}}


def member(member_id, tier_ids, user_id=None):
    relationships = {"currently_entitled_tiers": {"data": [{"type": "tier", "id": tier_id} for tier_id in tier_ids]}}
    if user_id is not None:
        relationships["user"] = {"data": {"type": "user", "id": user_id}}
    return {"type": "member", "id": member_id, "relationships": relationships}


def user(user_id, social_connections):
    return {"type": "user", "id": user_id, "attributes": {"social_connections": social_connections}}


def identity(included):
    return {"data": {"type": "user", "id": "1"}, "included": included}


class IdentityPaidTierTitleTests(SimpleTestCase):
    def test_not_a_member(self):
        self.assertIsNone(get_identity_paid_tier_title({"data": {"type": "user", "id": "1"}}))

    def test_member_without_entitled_tiers(self):
        self.assertIsNone(get_identity_paid_tier_title(identity([member("m1", [])])))

    def test_free_member(self):
        document = identity([member("m1", ["t0"]), tier("t0", "Free", 0)])
        self.assertIsNone(get_identity_paid_tier_title(document))

    def test_paid_member(self):
        document = identity([member("m1", ["t0", "t2"]), tier("t0", "Free", 0), tier("t2", "Gold", 1000)])
        self.assertEqual(get_identity_paid_tier_title(document), "Gold")

    def test_highest_paid_tier_wins(self):
        document = identity([member("m1", ["t1", "t2"]), tier("t1", "Bronze", 100), tier("t2", "Gold", 1000)])
        self.assertEqual(get_identity_paid_tier_title(document), "Gold")


class PatronDiscordUidsTests(SimpleTestCase):
    def test_only_patrons_with_discord_are_returned(self):
        members_page = {
            "data": [
                member("m1", ["t1"], user_id="u1"),
                member("m2", ["t0"], user_id="u2"),
                member("m3", [], user_id="u3"),
                member("m4", ["t1"], user_id="u4"),
                member("m5", ["t1"], user_id="u5"),
            ],
            "included": [
                tier("t0", "Free", 0),
                tier("t1", "Bronze", 100),
                user("u1", {"discord": {"user_id": "d1"}}),
                user("u2", {"discord": {"user_id": "d2"}}),
                user("u3", {"discord": {"user_id": "d3"}}),
                user("u4", {"discord": None}),
                user("u5", None),
            ],
        }
        self.assertEqual(get_patron_discord_uids(members_page), [{"patreon_user_id": "u1", "discord_uid": "d1"}])
