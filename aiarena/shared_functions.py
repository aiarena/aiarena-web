import re

def parse_tags(tags):
    """convert tags from single string to list if applicable, and then cleans the tags"""
    if isinstance(tags, str):
        tags = tags.lower().split(",")
    return [re.sub('[^a-z0-9 _]', '', tag.strip())[:32] for tag in tags if tag][:32]
