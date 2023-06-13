import fractions

from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from scipy.interpolate import lagrange


async def lagrange_chazhi(
    matcher: Matcher,
    arg: Message = CommandArg()
) -> None:
    msg = arg.extract_plain_text().strip()
    if msg == "":
        return
    msg = msg.split(" ")
    msg = [item.strip() for item in msg if item.strip()]
    if len(msg) < 2 or not all(item.isdigit() for item in msg):
        return
    
    
    msg = [int(item) for item in msg]
    x = list(range(1, len(msg) + 1))
    coeffs = lagrange_fraction(x, msg)
    func = ""
    count = len(coeffs)
    for i in coeffs:
        count -= 1
        if str(i) == "0":
            continue
        if count == 0:
            func += f"({str(i)})" if int(i) < 0 else str(i)
        elif count == 1:
            func += "x+" if str(i) == "1" else f"({str(i)})x+"
        else:
            func += f"x^{count}+" if str(i) == "1" else f"({str(i)})x^{count}+"
    if func[-1] == "+":
        func = func[:-1]
    await matcher.send(func)


def lagrange_fraction(x, y):
    p = lagrange(x, y)
    c = p.c
    d = p.order
    return [fractions.Fraction(c[i]).limit_denominator() for i in range(d + 1)]