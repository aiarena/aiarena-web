# Patreon integration

Talks to Patreon's API v2 (v1 was retired in October 2026). Two independent flows share it:

- **Per-user**: a user links their Patreon account via OAuth, and we periodically read *their* identity with *their* token to set their supporter level.
- **Creator**: with the campaign owner's own token we list the campaign's members, to find patrons who have connected Discord on Patreon but haven't linked their account here.

## What makes someone a patron

Both flows use one definition: **being currently entitled to a paid tier**. Membership alone isn't enough — free members and former patrons are members too — and a member's status string isn't what we key on. The supporter level is the entitled tier's title, lowercased, so the tier names on Patreon must match the levels the user model knows about.

## Invariants

- **An API failure must never read as "no pledge".** Losing a pledge eventually removes the user's supporter level, so error responses raise rather than being parsed as an empty result. The grace period exists on top of this because Patreon has been seen to transiently report real patrons as having no pledge.
- **Request only the scope we need.** The user OAuth flow asks for identity only. Without the broader memberships scope Patreon returns just the membership to *our* campaign, which is why the code doesn't have to filter memberships by campaign. Widening the scope would break that assumption.
- **v2 returns nothing by default.** Every attribute and relationship has to be requested explicitly, so a field that's read but not requested shows up as a missing key, not an empty value.
- **Tokens belong to the OAuth client that issued them.** Changing the client credentials orphans every stored user token and the creator refresh token.
