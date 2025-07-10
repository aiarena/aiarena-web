from rest_framework.reverse import reverse

from aiarena.core.s3_helpers import get_file_s3_url_with_content_disposition, is_s3_file


def get_bot_zip_url(bot, match_id, request=None, context=None):
    """
    Get the URL for a bot's zip file.

    Args:
        bot: The Bot instance
        match_id: The ID of the match
        request: The request object (required for non-S3 files)
        context: The serializer context (can be used instead of request for non-S3 files)

    Returns:
        str: URL to the bot zip file
    """
    if is_s3_file(bot.bot_zip):
        return get_file_s3_url_with_content_disposition(bot.bot_zip, f"{bot.name}.zip")
    else:
        from aiarena.core.models import MatchParticipation

        p = MatchParticipation.objects.only("participant_number").get(bot=bot, match_id=match_id)

        # Use the provided request or extract it from context
        req = request
        if req is None and context is not None:
            req = context.get("request")

        return reverse(
            "match-download-zip",
            kwargs={"pk": match_id, "p_num": p.participant_number},
            request=req,
        )


def get_bot_data_url(bot, match_id, request=None, context=None):
    """
    Get the URL for a bot's data file.

    Args:
        bot: The Bot instance
        match_id: The ID of the match
        request: The request object (required for non-S3 files)
        context: The serializer context (can be used instead of request for non-S3 files)

    Returns:
        str or None: URL to the bot data file, or None if the bot has no data
    """
    from aiarena.core.models import MatchParticipation

    p = (
        MatchParticipation.objects.select_related("bot")
        .only("use_bot_data", "bot__bot_data", "participant_number")
        .get(bot=bot, match_id=match_id)
    )

    if p.use_bot_data and p.bot.bot_data:
        if is_s3_file(bot.bot_data):
            return get_file_s3_url_with_content_disposition(bot.bot_data, f"{bot.name}_data.zip")
        else:
            # Use the provided request or extract it from context
            req = request
            if req is None and context is not None:
                req = context.get("request")

            return reverse(
                "match-download-data",
                kwargs={"pk": match_id, "p_num": p.participant_number},
                request=req,
            )
    else:
        return None
