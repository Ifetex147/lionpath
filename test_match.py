import re

nav_pattern = (
    r"\b("
    r"how\s+(?:do\s+i|can\s+i|to|goi|i)\s+(?:get|go|reach|find|locate|attend)|"
    r"how\s+goi\s+go|"
    r"go\s+(?:to|for)\s+(?:the\s+)?|"
    r"directions?\s+(?:to|for)|"
    r"from\s+.+?\s+to|"
    r"to\s+.+?\s+from|"
    r"where\s+(?:is|can\s+i\s+find|do\s+we\s+have|are|does)|"
    r"where\s+.+?\s+(?:hold|held|holding|take\s+place)|"
    r"venue\s+(?:for|of)|"
    r"route\s+to|"
    r"take\s+me\s+to|"
    r"path\s+to|"
    r"lead\s+me\s+to|"
    r"navigate\s+to|"
    r"way\s+to"
    r")\b"
)

m = re.search(nav_pattern, "how to do clerance")
if m:
    print("MATCHED:", m.group(0), m.groups())
else:
    print("NO MATCH")

