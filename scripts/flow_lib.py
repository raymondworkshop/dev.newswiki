"""Institutional flow heuristics from price + volume (accumulation / distribution)."""

from __future__ import annotations

import json
import math
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
USER_AGENT = "dev.business-flow/1.0 (personal research; +https://localhost)"

LOOKBACK_DAYS = 50
BUY_SCORE_WEEKS = 4  # buy remains short + strict (not the risk focus)
SELL_SCORE_WEEKS = 8  # primary risk window for distribution campaigns
ALERT_WEEKS = 4  # recent acceleration / early warning
RANGE_WEEKS = 13  # ~one quarter for support / resistance structure
VOL_AVG_WEEKS = 8
AVG_VOLUME_WINDOW = 50
HIGH_VOLUME_MULT = 1.3
HIGH_CLOSE_PCT = 0.70
LOW_CLOSE_PCT = 0.30
ZONE_PCT = 0.25
MIN_REPEAT_WEEKS = 2  # repeats before week footprints add meaningful score
STRONG_TOTAL_WEEKS = 3  # ≥3 total OR ≥2 consecutive → strong label
DISTRIBUTION_DAY_DROP = 0.002  # 0.2%
DISTRIBUTION_DAY_WINDOW = 15
# Risk-asymmetric weights: missing a sell is costlier than missing a buy
SELL_STRONG_SCORE = 3
SELL_REPEAT_SCORE = 2
SELL_WATCH_SCORE = 1  # single distribution week in sell window
BUY_STRONG_SCORE = 2
BUY_REPEAT_SCORE = 1
DIST_DAYS_WARN = 2  # mild risk score
DIST_DAYS_HEAVY = 3  # heavier risk score


@dataclass
class Bar:
    day: date
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class WeekBar:
    week_end: date
    high: float
    low: float
    close: float
    volume: float
    close_pct: float  # 0–1 within week's range
    vs_avg_volume: float


@dataclass
class FlowReport:
    ticker: str
    as_of: date
    bars: int
    up_down_volume_ratio: float | None
    avg_daily_volume: float
    accumulation_weeks: list[WeekBar] = field(default_factory=list)
    distribution_weeks: list[WeekBar] = field(default_factory=list)
    recent_weeks: list[WeekBar] = field(default_factory=list)
    alert_weeks: list[WeekBar] = field(default_factory=list)
    pullback_weeks_low_volume: int = 0
    pullback_weeks_high_volume: int = 0
    distribution_days: int = 0
    accum_consecutive: int = 0
    distrib_consecutive: int = 0
    buy_strong: bool = False
    sell_strong: bool = False
    sell_repeat: bool = False
    sell_watch: bool = False  # single sell week in 8w window
    sell_accelerating: bool = False  # sell footprint inside last ALERT_WEEKS
    risk_level: str = "none"  # none | watch | elevated | high
    range_low: float | None = None
    range_high: float | None = None
    accum_at_support: list[WeekBar] = field(default_factory=list)
    distrib_at_resistance: list[WeekBar] = field(default_factory=list)
    signal: str = "暂时没看到明显的大户卖出迹象"
    reasons: list[str] = field(default_factory=list)
    caveat: str = (
        "这只是用价钱和成交量粗粗看一眼，而且更在意「有没有人在卖」，不是叫你买或卖。"
        "成交量大，也不一定就是大机构；也可能只是很多人在短线买卖。"
        "大户若要卖，常常要卖好几个星期甚至几个月；这里主看近8周有没有卖出迹象，近4周还出没出现过。"
    )


def _http_get(url: str, timeout: float = 30.0) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_daily_bars(ticker: str, range_: str = "1y") -> list[Bar]:
    """Fetch daily OHLCV from Yahoo Finance chart API (stdlib only)."""
    symbol = ticker.strip().upper()
    if not symbol:
        raise ValueError("ticker is empty")

    qs = urllib.parse.urlencode({"interval": "1d", "range": range_})
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?{qs}"
    try:
        raw = _http_get(url)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Yahoo chart HTTP {exc.code} for {symbol}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Yahoo chart network error for {symbol}: {exc.reason}") from exc

    payload = json.loads(raw.decode("utf-8"))
    result = (payload.get("chart") or {}).get("result") or []
    if not result:
        err = (payload.get("chart") or {}).get("error") or {}
        raise RuntimeError(f"No chart data for {symbol}: {err.get('description') or err}")

    node = result[0]
    timestamps = node.get("timestamp") or []
    quote = ((node.get("indicators") or {}).get("quote") or [{}])[0]
    opens = quote.get("open") or []
    highs = quote.get("high") or []
    lows = quote.get("low") or []
    closes = quote.get("close") or []
    volumes = quote.get("volume") or []

    bars: list[Bar] = []
    for i, ts in enumerate(timestamps):
        o, h, l, c, v = (
            _num(opens, i),
            _num(highs, i),
            _num(lows, i),
            _num(closes, i),
            _num(volumes, i),
        )
        if None in (o, h, l, c, v) or c <= 0 or v < 0:
            continue
        day = datetime.fromtimestamp(int(ts), tz=timezone.utc).date()
        bars.append(Bar(day=day, open=o, high=h, low=l, close=c, volume=v))

    if len(bars) < LOOKBACK_DAYS:
        raise RuntimeError(f"Need ≥{LOOKBACK_DAYS} daily bars for {symbol}, got {len(bars)}")
    return bars


def _num(series: list[Any], i: int) -> float | None:
    if i >= len(series):
        return None
    val = series[i]
    if val is None:
        return None
    try:
        f = float(val)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return f


def up_down_volume_ratio(bars: list[Bar], lookback: int = LOOKBACK_DAYS) -> float | None:
    window = bars[-lookback:] if len(bars) >= lookback else bars
    if len(window) < 2:
        return None
    up_vol = 0.0
    down_vol = 0.0
    for i in range(1, len(window)):
        prev, cur = window[i - 1], window[i]
        if cur.close > prev.close:
            up_vol += cur.volume
        elif cur.close < prev.close:
            down_vol += cur.volume
    if down_vol <= 0:
        return None if up_vol <= 0 else float("inf")
    return up_vol / down_vol


def average_volume(bars: list[Bar], lookback: int = AVG_VOLUME_WINDOW) -> float:
    window = bars[-lookback:] if len(bars) >= lookback else bars
    if not window:
        return 0.0
    return sum(b.volume for b in window) / len(window)


def _iso_week_key(d: date) -> tuple[int, int]:
    iso = d.isocalendar()
    return iso.year, iso.week


def aggregate_weeks(bars: list[Bar]) -> list[WeekBar]:
    if not bars:
        return []
    groups: dict[tuple[int, int], list[Bar]] = {}
    order: list[tuple[int, int]] = []
    for b in bars:
        key = _iso_week_key(b.day)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(b)

    raw_weeks: list[tuple[date, float, float, float, float]] = []
    for key in order:
        g = groups[key]
        high = max(x.high for x in g)
        low = min(x.low for x in g)
        close = g[-1].close
        vol = sum(x.volume for x in g)
        raw_weeks.append((g[-1].day, high, low, close, vol))

    vols = [w[4] for w in raw_weeks]
    out: list[WeekBar] = []
    for i, (week_end, high, low, close, vol) in enumerate(raw_weeks):
        span = high - low
        close_pct = 0.5 if span <= 0 else max(0.0, min(1.0, (close - low) / span))
        # trailing average of prior weeks (exclude current)
        prior = vols[max(0, i - VOL_AVG_WEEKS) : i]
        avg = (sum(prior) / len(prior)) if prior else vol
        vs = (vol / avg) if avg > 0 else 1.0
        out.append(
            WeekBar(
                week_end=week_end,
                high=high,
                low=low,
                close=close,
                volume=vol,
                close_pct=close_pct,
                vs_avg_volume=vs,
            )
        )
    return out


def count_distribution_days(
    bars: list[Bar],
    avg_vol: float,
    window: int = DISTRIBUTION_DAY_WINDOW,
    drop: float = DISTRIBUTION_DAY_DROP,
    vol_mult: float = HIGH_VOLUME_MULT,
) -> int:
    if len(bars) < 2 or avg_vol <= 0:
        return 0
    segment = bars[-(window + 1) :]
    count = 0
    for i in range(1, len(segment)):
        prev, cur = segment[i - 1], segment[i]
        chg = (cur.close - prev.close) / prev.close if prev.close else 0.0
        if chg <= -drop and cur.volume >= avg_vol * vol_mult:
            count += 1
    return count


def max_consecutive(flags: list[bool]) -> int:
    best = cur = 0
    for flag in flags:
        if flag:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def is_buy_week(w: WeekBar) -> bool:
    return w.close_pct >= HIGH_CLOSE_PCT and w.vs_avg_volume >= HIGH_VOLUME_MULT


def is_sell_week(w: WeekBar) -> bool:
    return w.close_pct <= LOW_CLOSE_PCT and w.vs_avg_volume >= HIGH_VOLUME_MULT


def trading_range(weeks: list[WeekBar]) -> tuple[float | None, float | None]:
    if not weeks:
        return None, None
    return min(w.low for w in weeks), max(w.high for w in weeks)


def near_support(w: WeekBar, range_low: float, range_high: float) -> bool:
    span = range_high - range_low
    if span <= 0:
        return False
    ceiling = range_low + ZONE_PCT * span
    return w.low <= ceiling


def near_resistance(w: WeekBar, range_low: float, range_high: float) -> bool:
    span = range_high - range_low
    if span <= 0:
        return False
    floor = range_high - ZONE_PCT * span
    return w.high >= floor


def footprint_stats(weeks: list[WeekBar]) -> tuple[list[WeekBar], list[WeekBar], int, int]:
    buy_flags = [is_buy_week(w) for w in weeks]
    sell_flags = [is_sell_week(w) for w in weeks]
    accum = [w for w, flag in zip(weeks, buy_flags) if flag]
    distrib = [w for w, flag in zip(weeks, sell_flags) if flag]
    return accum, distrib, max_consecutive(buy_flags), max_consecutive(sell_flags)


def is_strong_repeat(count: int, consecutive: int) -> bool:
    """Strong weekly evidence: ≥2 weeks AND (consecutive ≥2 OR total ≥3)."""
    if count < MIN_REPEAT_WEEKS:
        return False
    return consecutive >= MIN_REPEAT_WEEKS or count >= STRONG_TOTAL_WEEKS


def evaluate_flow(ticker: str, bars: list[Bar]) -> FlowReport:
    symbol = ticker.strip().upper()
    ratio = up_down_volume_ratio(bars)
    avg_vol = average_volume(bars)
    weeks = aggregate_weeks(bars)
    buy_window = weeks[-BUY_SCORE_WEEKS:] if weeks else []
    sell_window = weeks[-SELL_SCORE_WEEKS:] if weeks else []
    alert_window = weeks[-ALERT_WEEKS:] if weeks else []
    range_weeks = weeks[-RANGE_WEEKS:] if weeks else []
    range_low, range_high = trading_range(range_weeks)

    accum, _, accum_consec, _ = footprint_stats(buy_window)
    _, distrib, _, distrib_consec = footprint_stats(sell_window)
    alert_distrib = [w for w in alert_window if is_sell_week(w)]

    buy_repeat = len(accum) >= MIN_REPEAT_WEEKS or accum_consec >= MIN_REPEAT_WEEKS
    sell_repeat = len(distrib) >= MIN_REPEAT_WEEKS or distrib_consec >= MIN_REPEAT_WEEKS
    buy_strong = is_strong_repeat(len(accum), accum_consec)
    sell_strong = is_strong_repeat(len(distrib), distrib_consec)
    sell_watch = len(distrib) == 1 and not sell_repeat
    sell_accelerating = bool(alert_distrib)

    accum_at_support: list[WeekBar] = []
    distrib_at_resistance: list[WeekBar] = []
    if range_low is not None and range_high is not None:
        accum_at_support = [w for w in accum if near_support(w, range_low, range_high)]
        distrib_at_resistance = [
            w for w in distrib if near_resistance(w, range_low, range_high)
        ]

    # pullbacks: in sell window, weeks that closed lower vs prior week
    low_vol_pb = 0
    high_vol_pb = 0
    for i in range(1, len(sell_window)):
        prev, cur = sell_window[i - 1], sell_window[i]
        if cur.close < prev.close:
            if cur.vs_avg_volume < 1.0:
                low_vol_pb += 1
            elif cur.vs_avg_volume >= HIGH_VOLUME_MULT:
                high_vol_pb += 1

    dist_days = count_distribution_days(bars, avg_vol)

    # Negative score = more sell/risk pressure
    score = 0
    reasons: list[str] = []
    reasons.append(
        f"怎么看：更在意「有没有人在卖」。主看近{SELL_SCORE_WEEKS}周有没有卖出迹象；"
        f"近{ALERT_WEEKS}周看最近还出没出现过。"
        f"买的迹象只作参考（近{BUY_SCORE_WEEKS}周，而且要求更严）。"
    )

    # Daily ratio is auxiliary (±1), not enough alone for a strong call
    if ratio is None:
        reasons.append(
            f"近{LOOKBACK_DAYS}天里，没法比较「涨的日子」和「跌的日子」谁成交更多（数据不够）。"
        )
    elif math.isinf(ratio):
        score += 1
        reasons.append(
            f"近{LOOKBACK_DAYS}天几乎都是涨的时候成交特别多（只能当旁证，偏买）。"
        )
    else:
        if ratio >= 2.0:
            score += 1
            reasons.append(
                f"近{LOOKBACK_DAYS}天：涨的日子成交量大约是跌的日子的 {ratio:.1f} 倍"
                f"（数字 {ratio:.2f}≥2，旁证偏买）。单靠这个还不够下结论。"
            )
        elif ratio < 1.0:
            score -= 1
            reasons.append(
                f"近{LOOKBACK_DAYS}天：跌的日子成交量更大"
                f"（数字 {ratio:.2f}<1，旁证偏卖）。单靠这个还不够下结论。"
            )
        else:
            reasons.append(
                f"近{LOOKBACK_DAYS}天：涨跌两日成交量差不多（数字 {ratio:.2f}，接近 1）。"
            )

    # --- Sell side (asymmetric, heavier) ---
    if sell_strong:
        score -= SELL_STRONG_SCORE
        last = distrib[-1]
        reasons.append(
            f"近{SELL_SCORE_WEEKS}周「更像有人在卖」出现得比较密：共 {len(distrib)} 周，"
            f"最多连着 {distrib_consec} 周。"
            f"最近一次到 {last.week_end}：收盘靠近本周低位（约 {last.close_pct:.0%}），"
            f"成交大约是平时的 {last.vs_avg_volume:.1f} 倍。"
        )
    elif sell_repeat:
        score -= SELL_REPEAT_SCORE
        last = distrib[-1]
        reasons.append(
            f"近{SELL_SCORE_WEEKS}周「更像有人在卖」出现了不止一次"
            f"（共 {len(distrib)} 周，最多连着 {distrib_consec} 周），"
            f"但还没密到「连着≥{MIN_REPEAT_WEEKS}周或总共≥{STRONG_TOTAL_WEEKS}周」。"
            f"最近一次到 {last.week_end}。要多留个心眼。"
        )
    elif sell_watch:
        score -= SELL_WATCH_SCORE
        last = distrib[-1]
        reasons.append(
            f"近{SELL_SCORE_WEEKS}周只有 1 周更像「有人在卖」（到 {last.week_end}）。"
            f"一周还不算大事，但先记一笔黄灯。"
        )
    else:
        reasons.append(
            f"近{SELL_SCORE_WEEKS}周没有「收在低位 + 成交明显变大」的卖出周。"
        )

    if sell_accelerating and distrib:
        reasons.append(
            f"近{ALERT_WEEKS}周里又出现了卖出迹象（{len(alert_distrib)} 周）——"
            f"不是很久以前的旧痕迹，最近还在。"
        )
    elif distrib and not sell_accelerating:
        reasons.append(
            f"近{ALERT_WEEKS}周没有新的卖出周；迹象主要在更早几周——"
            f"近{SELL_SCORE_WEEKS}周仍要算进去，但不像最近刚又冒出来。"
        )

    # --- Buy side (stricter, lighter weight) ---
    if buy_strong:
        score += BUY_STRONG_SCORE
        last = accum[-1]
        reasons.append(
            f"近{BUY_SCORE_WEEKS}周「更像有人在买」出现得比较密（只作参考）：共 {len(accum)} 周，"
            f"最多连着 {accum_consec} 周。最近一次到 {last.week_end}。"
        )
    elif buy_repeat:
        score += BUY_REPEAT_SCORE
        last = accum[-1]
        reasons.append(
            f"近{BUY_SCORE_WEEKS}周「更像有人在买」出现了不止一次（只作参考，共 {len(accum)} 周），"
            f"但还不够密。最近一次到 {last.week_end}。"
        )
    elif accum:
        last = accum[-1]
        reasons.append(
            f"近{BUY_SCORE_WEEKS}周只有 {len(accum)} 周更像「有人在买」"
            f"（到 {last.week_end}）。买的迹象单周不加分。"
        )
    else:
        reasons.append(
            f"近{BUY_SCORE_WEEKS}周没有「收在高位 + 成交明显变大」的买入周。"
        )

    if range_low is not None and range_high is not None:
        reasons.append(
            f"近{RANGE_WEEKS}周价钱大致在 {range_low:.2f}～{range_high:.2f}。"
            f"靠下方约 1/4 像「容易被托住」的低位一带；靠上方约 1/4 像「不太容易再往上冲」的高位一带。"
        )
        if distrib_at_resistance and sell_strong:
            score -= 1
            reasons.append(
                f"卖出周里，有 {len(distrib_at_resistance)} 周落在高位一带附近，更像涨不动时有人往外倒。"
            )
        elif distrib_at_resistance and (sell_repeat or sell_watch):
            score -= 1
            reasons.append(
                f"卖出周里已有 {len(distrib_at_resistance)} 周落在高位一带附近；多记一笔压力。"
            )
        elif distrib_at_resistance:
            reasons.append("卖出周有落在高位一带附近，迹象还弱，不加分。")
        else:
            reasons.append("近几周没有「高位一带 + 成交变大 + 收在低位」这种卖法。")

        if accum_at_support and buy_strong:
            score += 1
            reasons.append(
                f"买入周里，有 {len(accum_at_support)} 周落在低位一带附近（只作参考）。"
            )
        elif accum_at_support:
            reasons.append("买入周有落在低位一带，但买的迹象还不够密，只作参考、暂不加分。")
        else:
            reasons.append("近几周没有「低位一带 + 成交变大 + 收在高位」这种买法。")

    if low_vol_pb and not high_vol_pb:
        score += 1
        reasons.append(
            f"近{SELL_SCORE_WEEKS}周里价钱往下走的周，成交大多不大"
            f"（轻量往下 {low_vol_pb}、放量往下 {high_vol_pb}）。更像歇一歇，不像急着卖。"
        )
    elif high_vol_pb and high_vol_pb >= low_vol_pb:
        score -= 1
        reasons.append(
            f"近{SELL_SCORE_WEEKS}周往下走的周里，成交变大的更多"
            f"（放量往下 {high_vol_pb}、轻量往下 {low_vol_pb}）。更像跌的时候也有人在卖。"
        )

    if dist_days >= DIST_DAYS_HEAVY:
        score -= 2
        reasons.append(
            f"近{DISTRIBUTION_DAY_WINDOW}天有 {dist_days} 天「跌得比较明显，而且成交很大」"
            f"（已经 ≥{DIST_DAYS_HEAVY} 次，要更当心）。"
        )
    elif dist_days >= DIST_DAYS_WARN:
        score -= 1
        reasons.append(
            f"近{DISTRIBUTION_DAY_WINDOW}天有 {dist_days} 天「跌得比较明显，而且成交很大」"
            f"（已经 ≥{DIST_DAYS_WARN} 次，先提个醒）。"
        )
    elif dist_days == 1:
        reasons.append(
            f"近{DISTRIBUTION_DAY_WINDOW}天只有 {dist_days} 天「跌得多且成交大」；一天还不算什么。"
        )
    else:
        reasons.append(
            f"近{DISTRIBUTION_DAY_WINDOW}天没有「跌得多且成交大」的日子。"
        )

    # Ambiguous: both buy and sell footprints → lean defensive
    both_sides = bool(accum) and bool(distrib)
    if both_sides:
        score -= 1
        reasons.append(
            "同一段时间里，买的迹象和卖的迹象都有；更在意风险时，先当成「可能有人在卖」，不要互相抵消当没事。"
        )

    signal, risk_level = _risk_signal(
        score=score,
        sell_strong=sell_strong,
        sell_repeat=sell_repeat,
        sell_watch=sell_watch,
        sell_accelerating=sell_accelerating,
        buy_strong=buy_strong,
        has_distrib=bool(distrib),
        has_accum=bool(accum),
        dist_days=dist_days,
        both_sides=both_sides,
    )

    return FlowReport(
        ticker=symbol,
        as_of=bars[-1].day,
        bars=len(bars),
        up_down_volume_ratio=ratio,
        avg_daily_volume=avg_vol,
        accumulation_weeks=accum,
        distribution_weeks=distrib,
        recent_weeks=sell_window,
        alert_weeks=alert_window,
        pullback_weeks_low_volume=low_vol_pb,
        pullback_weeks_high_volume=high_vol_pb,
        distribution_days=dist_days,
        accum_consecutive=accum_consec,
        distrib_consecutive=distrib_consec,
        buy_strong=buy_strong,
        sell_strong=sell_strong,
        sell_repeat=sell_repeat,
        sell_watch=sell_watch,
        sell_accelerating=sell_accelerating,
        risk_level=risk_level,
        range_low=range_low,
        range_high=range_high,
        accum_at_support=accum_at_support,
        distrib_at_resistance=distrib_at_resistance,
        signal=signal,
        reasons=reasons,
    )


def _risk_signal(
    *,
    score: int,
    sell_strong: bool,
    sell_repeat: bool,
    sell_watch: bool,
    sell_accelerating: bool,
    buy_strong: bool,
    has_distrib: bool,
    has_accum: bool,
    dist_days: int,
    both_sides: bool,
) -> tuple[str, str]:
    """Return (signal text, risk_level). Prefer defensive wording."""
    if sell_strong or score <= -SELL_STRONG_SCORE:
        msg = "要当心：更像有人在卖，而且出现得比较密"
        if sell_accelerating:
            msg = "要当心：更像有人在卖，而且最近几周还在出现"
        return msg, "high"

    if sell_repeat or (has_distrib and score <= -SELL_REPEAT_SCORE):
        msg = "多留个心眼：卖出迹象出现了不止一次"
        if sell_accelerating:
            msg = "多留个心眼：卖出迹象不止一次，而且最近几周还在"
        return msg, "elevated"

    if sell_watch or dist_days >= DIST_DAYS_WARN or (both_sides and has_distrib):
        if sell_watch and sell_accelerating:
            return "多留个心眼：最近几周出现过一周「更像有人在卖」", "watch"
        if dist_days >= DIST_DAYS_WARN and not has_distrib:
            return "多留个心眼：最近几天有过「跌得多且成交大」", "watch"
        if both_sides:
            return "多留个心眼：又像有人买、又像有人卖，先当可能有人在卖", "watch"
        return "多留个心眼：有一点卖出迹象，但还不密", "watch"

    if buy_strong and score >= BUY_STRONG_SCORE and not has_distrib:
        return "暂时没看到明显的大户卖出；倒是有些买入迹象（只作参考）", "none"

    if score >= 1 and not has_distrib:
        return "暂时没看到明显的大户卖出迹象", "none"

    if has_distrib:
        return "多留个心眼：能看到一点卖出迹象", "watch"

    return "暂时没看到明显的大户卖出迹象", "none"


def _fmt_ratio(ratio: float | None) -> str:
    if ratio is None:
        return "n/a"
    if math.isinf(ratio):
        return "∞"
    return f"{ratio:.2f}"


def judgment_rules() -> list[str]:
    return [
        f"更在意卖出：主看近 {SELL_SCORE_WEEKS} 周有没有「更像有人在卖」；"
        f"近 {ALERT_WEEKS} 周看最近还出没出现过。"
        f"买入只作参考（近 {BUY_SCORE_WEEKS} 周，要求更严）。",
        f"卖出：出现 1 周就亮黄灯；"
        f"出现不止一次要更当心；"
        f"连着≥{MIN_REPEAT_WEEKS}周或总共≥{STRONG_TOTAL_WEEKS}周，就算比较密。",
        f"买入：至少 {MIN_REPEAT_WEEKS} 周才加分；就算买得很密，权重也比卖的轻。"
        "又像买又像卖时，先当可能有人在卖，不要互相抵消。",
        "「更像在卖」的一周：收盘靠近本周最低价"
        f"（大概只到本周从低到高的 {int(LOW_CLOSE_PCT * 100)}% 及以下），成交至少是平时的 {HIGH_VOLUME_MULT} 倍。",
        "「更像在买」的一周：收盘靠近本周最高价"
        f"（大概要到本周从低到高的 {int(HIGH_CLOSE_PCT * 100)}% 以上），成交至少是平时的 {HIGH_VOLUME_MULT} 倍。",
        f"近 {RANGE_WEEKS} 周价钱高低：下方约 {int(ZONE_PCT * 100)}% 算低位一带，"
        f"上方约 {int(ZONE_PCT * 100)}% 算高位一带；在高位一带还放量收低，多记一笔压力。",
        f"近 {LOOKBACK_DAYS} 天「涨日成交 ÷ 跌日成交」只是旁证；"
        f"近 {DISTRIBUTION_DAY_WINDOW} 天「跌得多且成交大」："
        f"{DIST_DAYS_WARN} 次起提个醒，≥{DIST_DAYS_HEAVY} 次更当心。",
    ]


def build_markdown(report: FlowReport) -> str:
    ratio_txt = _fmt_ratio(report.up_down_volume_ratio)
    risk_label = {
        "none": "暂时放心",
        "watch": "留个心眼",
        "elevated": "要多当心",
        "high": "比较当心",
    }.get(report.risk_level, report.risk_level)
    alert_ends = {w.week_end for w in report.alert_weeks}
    lines = [
        f"# {report.ticker}：最近是不是更像有人在卖？",
        "",
        f"**结论: {report.signal}**",
        f"**当心程度: {risk_label}**",
        "",
        "## 理由",
    ]
    lines.extend(f"- {r}" for r in report.reasons)
    lines.extend(["", "## 怎么判断的"])
    lines.extend(f"- {r}" for r in judgment_rules())
    lines.extend(
        [
            "",
            "## 数字摘要",
            f"- 数据算到: {report.as_of}",
            f"- 一共用了多少天的价钱: {report.bars}",
            f"- 近{LOOKBACK_DAYS}天：涨的日子成交量 ÷ 跌的日子成交量 = {ratio_txt}"
            f"（大于 2 更像买得积极；小于 1 更像卖得积极；接近 1 差不多）",
            f"- 近{AVG_VOLUME_WINDOW}天平均每天成交多少: {report.avg_daily_volume:,.0f}",
            f"- 近{SELL_SCORE_WEEKS}周「更像在卖」: {len(report.distribution_weeks)} 周"
            f"（最多连着 {report.distrib_consecutive} 周；"
            f"算比较密吗 {'是' if report.sell_strong else '否'}；"
            f"只有单周黄灯吗 {'是' if report.sell_watch else '否'}；"
            f"近{ALERT_WEEKS}周还出现过吗 {'是' if report.sell_accelerating else '否'}）",
            f"- 近{BUY_SCORE_WEEKS}周「更像在买」（只作参考）: {len(report.accumulation_weeks)} 周"
            f"（最多连着 {report.accum_consecutive} 周；算比较密吗 {'是' if report.buy_strong else '否'}）",
            (
                f"- 近{RANGE_WEEKS}周价钱区间: {report.range_low:.2f}～{report.range_high:.2f}"
                if report.range_low is not None and report.range_high is not None
                else "- 近几周价钱区间: 暂无"
            ),
            f"- 买在低位一带 / 卖在高位一带: "
            f"{len(report.accum_at_support)} / {len(report.distrib_at_resistance)}",
            f"- 近{DISTRIBUTION_DAY_WINDOW}天「跌得多且成交大」: {report.distribution_days} 天",
        ]
    )

    if report.recent_weeks:
        lines.extend(
            [
                "",
                f"## 近{SELL_SCORE_WEEKS}周一览（近{ALERT_WEEKS}周标成「最近」）",
                "",
                "| 周结束日 | 收盘价 | 收盘有多靠近本周最高价 | 成交量是平时的几倍 | 怎么看 |",
                "| --- | ---: | ---: | ---: | --- |",
            ]
        )
        for w in report.recent_weeks:
            tags: list[str] = []
            if w.week_end in alert_ends:
                tags.append("最近")
            if is_buy_week(w):
                tags.append("更像在买")
            if is_sell_week(w):
                tags.append("更像在卖")
            if w in report.accum_at_support:
                tags.append("靠近低位一带")
            if w in report.distrib_at_resistance:
                tags.append("靠近高位一带")
            tag = "；".join(tags)
            near = (
                "很靠近最高"
                if w.close_pct >= HIGH_CLOSE_PCT
                else ("很靠近最低" if w.close_pct <= LOW_CLOSE_PCT else "在中间附近")
            )
            lines.append(
                f"| {w.week_end} | {w.close:.2f} | {w.close_pct:.0%}（{near}） | "
                f"{w.vs_avg_volume:.2f} 倍 | {tag} |"
            )

    lines.extend(
        [
            "",
            f"> {report.caveat}",
            "",
            f"若想看公司赚钱情况等，可另跑: `make analyze TICKER={report.ticker}`",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(report: FlowReport, output_dir: Path | None = None) -> Path:
    target = output_dir or OUTPUT_DIR
    target.mkdir(parents=True, exist_ok=True)
    path = target / f"{report.ticker}_flow.md"
    path.write_text(build_markdown(report), encoding="utf-8")
    return path


def run_flow(
    ticker: str, range_: str = "1y", output_dir: Path | None = None
) -> tuple[Path, FlowReport]:
    bars = fetch_daily_bars(ticker, range_=range_)
    report = evaluate_flow(ticker, bars)
    path = write_report(report, output_dir=output_dir)
    return path, report
