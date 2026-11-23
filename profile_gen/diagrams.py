"""The little architecture drawings from the approved mockup, one per `diagram` key.

All are drawn in a 300x70 box with four classes defined by the card stylesheet:
  s  accent stroke, no fill      f  accent fill
  m  muted mono label            g  neutral hairline
"""

from __future__ import annotations

DIAGRAMS: dict[str, str] = {
    "starport": (
        '<rect class="s" x="4" y="22" width="52" height="26" rx="3"/>'
        '<text class="m" x="14" y="39">bots</text>'
        '<path class="s" d="M56 35h40" stroke-dasharray="3 3"/>'
        '<text class="m" x="62" y="18">spsc</text>'
        '<rect class="s" x="96" y="22" width="66" height="26" rx="3"/>'
        '<text class="m" x="103" y="39">matcher</text>'
        '<path class="s" d="M162 35h24"/>'
        '<g class="f"><rect x="190" y="6" width="30" height="6"/><rect x="190" y="14" width="46" height="6"/>'
        '<rect x="190" y="22" width="22" height="6"/><rect x="190" y="42" width="38" height="6"/>'
        '<rect x="190" y="50" width="54" height="6"/><rect x="190" y="58" width="26" height="6"/></g>'
        '<path class="g" d="M186 35h70"/>'
        '<text class="m" x="262" y="20">asks</text>'
        '<text class="m" x="262" y="58">bids</text>'
    ),
    "enclave": (
        '<rect class="s" x="4" y="22" width="62" height="26" rx="3"/>'
        '<text class="m" x="13" y="39">pwa</text>'
        '<rect class="s" x="118" y="22" width="70" height="26" rx="3"/>'
        '<text class="m" x="124" y="39">gatekeeper</text>'
        '<rect class="s" x="234" y="22" width="62" height="26" rx="3"/>'
        '<text class="m" x="240" y="39">matrix</text>'
        '<path class="s" d="M66 35h52M188 35h46" stroke-dasharray="3 3"/>'
        '<text class="m" x="74" y="18">e2ee</text>'
        '<text class="m" x="194" y="18">invite</text>'
    ),
    "parallax": (
        '<path class="g" d="M0 60h300"/>'
        '<path class="g" d="M228 60v-46" stroke-dasharray="2 3"/>'
        '<path class="s" d="M8 52 Q70 -6 132 60 Q175 22 216 60"/>'
        '<path class="s" d="M216 60 Q240 44 262 60" stroke-dasharray="3 3"/>'
        '<circle class="f" cx="70" cy="23" r="2.5"/>'
        '<circle class="f" cx="132" cy="60" r="2.5"/>'
        '<circle class="f" cx="216" cy="60" r="3.5"/>'
        '<text class="m" x="232" y="22">line</text>'
        '<text class="m" x="266" y="54">in?</text>'
    ),
    "meridian": (
        '<g class="m"><text x="0" y="12">train</text><text x="0" y="66">test</text></g>'
        '<g class="s"><rect x="40" y="4" width="60" height="10"/>'
        '<rect x="104" y="56" width="20" height="10"/>'
        '<rect x="40" y="18" width="80" height="10"/>'
        '<rect x="124" y="56" width="20" height="10"/>'
        '<rect x="40" y="32" width="100" height="10"/>'
        '<rect x="144" y="56" width="20" height="10"/></g>'
        '<path class="g" d="M184 8v58"/>'
        '<text class="m" x="192" y="20">HMM regimes</text>'
        '<text class="m" x="192" y="36">deflated Sharpe</text>'
        '<text class="m" x="192" y="52">bootstrap CIs</text>'
    ),
    "conduit": (
        '<g class="s"><rect x="4" y="22" width="58" height="26" rx="3"/>'
        '<rect x="84" y="22" width="58" height="26" rx="3"/>'
        '<rect x="164" y="22" width="58" height="26" rx="3"/>'
        '<rect x="244" y="22" width="52" height="26" rx="3"/>'
        '<path d="M62 35h22M142 35h22M222 35h22"/></g>'
        '<g class="m"><text x="12" y="39">api</text><text x="92" y="39">bronze</text>'
        '<text x="172" y="39">silver</text><text x="252" y="39">gold</text></g>'
        '<g class="f"><circle cx="153" cy="35" r="3"/><circle cx="233" cy="35" r="3"/></g>'
        '<text class="m" x="128" y="64">quality gates</text>'
    ),
    "quorum": (
        '<g class="s"><circle cx="40" cy="35" r="16"/><circle cx="100" cy="14" r="10"/>'
        '<circle cx="100" cy="56" r="10"/><circle cx="160" cy="14" r="10"/>'
        '<circle cx="160" cy="56" r="10"/>'
        '<path d="M55 29l36-12M55 41l36 12M56 33l94-17M56 37l94 17" stroke-dasharray="2 3"/></g>'
        '<path class="g" d="M190 0v70" stroke-dasharray="4 3"/>'
        '<text class="m" x="40" y="38" text-anchor="middle">lead</text>'
        '<text class="m" x="200" y="22">partition</text>'
        '<text class="m" x="200" y="38">crash · drop</text>'
        '<text class="m" x="200" y="54">linearizable ✓</text>'
    ),
    "wrecker": (
        '<g class="s"><rect x="4" y="22" width="56" height="26" rx="3"/>'
        '<rect x="84" y="22" width="56" height="26" rx="3"/>'
        '<rect x="164" y="22" width="56" height="26" rx="3"/>'
        '<rect x="244" y="22" width="52" height="26" rx="3"/>'
        '<path d="M60 35h24M140 35h24M220 35h24"/></g>'
        '<g class="m"><text x="12" y="39">react</text><text x="92" y="39">flask</text>'
        '<text x="168" y="39">llm api</text><text x="250" y="39">azure</text></g>'
    ),
}
