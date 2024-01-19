
import common_lib


# ------------------------- Checks for keywords in text -----------------

def keyword_partition(text, delim):
    if isinstance(text, str) is True:
        return text.partition(delim)[0]


def keyword_check(text):
    keywords = common_lib.read_from_txt("keyword_check/keywords.txt")
    negatives = common_lib.read_from_txt("keyword_check/negatives.txt")
    delim = "@Deal Notifications"

    if keywords:
        for keyword_set in keywords:
            good = False
            matches = 0
            total = len(keyword_set.split("+"))
            for keyword in keyword_set.split("+"):
                if isinstance(text, str) is True:
                    text_part = keyword_partition(text, delim)
                    if (keyword.lower() in text_part.lower()):
                        matches += 1
                elif hasattr(text, "content"):
                    text_content_part = keyword_partition(text.content, delim)
                    if (keyword.lower() in text_content_part.lower()):
                        matches += 1
                    elif text.embeds:
                        embed_full = ""
                        if text.embeds[0].title:
                            embed_full += text.embeds[0].title
                        if text.embeds[0].description:
                            embed_full += text.embeds[0].description
                        embed_full_part = keyword_partition(embed_full, delim)
                        if (keyword.lower() in embed_full_part.lower()):
                            matches += 1
            if (matches == total):
                good = True
                break

        if negatives:
            for negative in negatives:
                if isinstance(text, str) is True:
                    text_part = keyword_partition(text, delim)
                    if (negative.lower() in text_part.lower()):
                        good = False
                        break
                if hasattr(text, "content"):
                    text_content_part = keyword_partition(text.content, delim)
                    if (negative.lower() in text_content_part.lower()):
                        good = False
                        break
                    elif text.embeds:
                        embed_full = ""
                        if text.embeds[0].title:
                            embed_full += text.embeds[0].title
                        if text.embeds[0].description:
                            embed_full += text.embeds[0].description
                        embed_full_part = keyword_partition(embed_full, delim)
                        if (negative.lower() in embed_full_part.lower()):
                            good = False
                            break

        if (good):
            return (True, keyword_set)
        else:
            return (False, None)
    else:
        return (False, None)
