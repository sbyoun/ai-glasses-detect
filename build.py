#!/usr/bin/env python3
"""data/*.yaml 을 읽어 정적 사이트(site/)를 만든다. 의존성: PyYAML."""
import html
import json
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
DATA = ROOT / "data"
OUT = ROOT / "site"
BASE = "https://glasses.foldalpha.com"
REPO = "https://github.com/sbyoun/ai-glasses-detect"


def load(name):
    return yaml.safe_load((DATA / name).read_text(encoding="utf-8"))


def e(s):
    return html.escape(str(s)) if s is not None else ""


def hexid(n):
    return f"0x{n:04X}"


KR_SALES = {"official": "국내 정식 판매", "import": "직구로만", "unknown": "확인 안 됨"}
DETECT = {"yes": ("○", "안경 전용 ID 등록"), "partial": ("△", "폰·이어폰과 ID 공유"),
          "no": ("✕", "SIG 미등록"), None: ("?", "확인 안 됨")}

CSS = """
:root{--bg:#fff;--fg:#1a1a1a;--mute:#666;--line:#e3e3e3;--acc:#0a58ca;--warn:#b42318;--ok:#067647}
@media (prefers-color-scheme:dark){:root{--bg:#111;--fg:#eee;--mute:#9a9a9a;--line:#2c2c2c;--acc:#6ea8fe;--warn:#f97066;--ok:#47cd89}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.65 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Noto Sans KR",sans-serif}
main{max-width:960px;margin:0 auto;padding:24px 16px 64px}a{color:var(--acc)}
nav{display:flex;gap:16px;flex-wrap:wrap;font-size:14px;border-bottom:1px solid var(--line);padding-bottom:12px;margin-bottom:24px}
h1{font-size:26px;line-height:1.35;margin:0 0 8px}h2{font-size:20px;margin:36px 0 12px}
.lead{color:var(--mute);margin:0 0 20px}.mute{color:var(--mute);font-size:14px}
.tw{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:14px}
th,td{border-bottom:1px solid var(--line);padding:8px 6px;text-align:left;vertical-align:top}th{white-space:nowrap}
.y{color:var(--ok);font-weight:600}.n{color:var(--warn);font-weight:600}
ul{padding-left:20px}footer{margin-top:48px;font-size:13px;color:var(--mute);border-top:1px solid var(--line);padding-top:12px}
code{font-size:13px}
"""


def page(path, title, desc, body, jsonld=None):
    url = BASE + path
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="naver-site-verification" content="d63c61747cc51e71a70f7a7589e2bfa66f4a5662" />
<style>{CSS}</style>{ld}</head><body><main>
<nav><a href="/">AI 안경 식별 DB</a><a href="/methods/">탐지 방법</a><a href="/ble-ids/">블루투스 제조사 ID</a><a href="/incidents/">적발 사례</a><a href="{REPO}">GitHub</a></nav>
{body}
<footer>공개 자료만 모은 데이터베이스입니다. 실기기 측정값은 없고, 모르는 값은 비워 두었습니다. 데이터 CC BY 4.0 · 코드 MIT ·
수정 제안은 <a href="{REPO}/issues">GitHub 이슈</a>로. 원본: <a href="/data/glasses.json">glasses.json</a> · <a href="/data/ble-company-ids.json">ble-company-ids.json</a> · <a href="/data/incidents.json">incidents.json</a> · <a href="/data/methods.json">methods.json</a></footer>
</main></body></html>"""
    f = OUT / path.lstrip("/") / "index.html"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(doc, encoding="utf-8")
    return url


def srcs(lst):
    return "<ul>" + "".join(f'<li><a href="{e(u)}">{e(u)}</a></li>' for u in lst) + "</ul>"


def cam(m):
    c = m.get("camera") or {}
    if c.get("present") is True:
        return "있음" + (f" ({e(c['spec'])})" if c.get("spec") else "")
    if c.get("present") is False:
        return "없음" + (f" ({e(c['spec'])})" if c.get("spec") else "")
    return "확인 안 됨"


def disp(m):
    d = m.get("display")
    if not d:
        return "없음"
    return e(d.get("type")) + (f" ({e(d['spec'])})" if d.get("spec") else "")


def ble_cell(m):
    b = m.get("ble") or {}
    mark, why = DETECT.get(b.get("detectable"))
    cls = "y" if b.get("detectable") == "yes" else "n" if b.get("detectable") == "no" else ""
    ids = ", ".join(hexid(i) for i in b.get("ids") or []) or "-"
    return f'<span class="{cls}">{mark}</span> {e(why)}<br><code>{ids}</code>'


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    glasses = load("glasses.yaml")["models"]
    ble = load("ble-company-ids.yaml")
    inc = load("incidents.yaml")
    meth = load("methods.yaml")["methods"]
    urls = []

    # 원본 데이터(JSON) — 기계가 읽기 쉽게
    (OUT / "data").mkdir()
    for name, obj in [("glasses", {"models": glasses}), ("ble-company-ids", ble), ("incidents", inc), ("methods", {"methods": meth})]:
        def conv(o):
            if isinstance(o, dict):
                return {k: conv(v) for k, v in o.items()}
            if isinstance(o, list):
                return [conv(v) for v in o]
            return o.isoformat() if hasattr(o, "isoformat") else o
        o = conv(obj)
        if name == "ble-company-ids":
            for x in o["ids"]:
                x["id"] = hexid(x["id"])
        if name == "glasses":
            for m in o["models"]:
                m["ble"]["ids"] = [hexid(i) for i in m["ble"]["ids"]]
        (OUT / "data" / f"{name}.json").write_text(json.dumps(o, ensure_ascii=False, indent=1), encoding="utf-8")

    # 모델 상세
    for m in glasses:
        rows = [("제조사", e(m["maker"])), ("카메라", cam(m)), ("화면", disp(m)),
                ("무게", f"{m['weight_g']}g" + (f" ({e(m['weight_note'])})" if m.get("weight_note") else "") if m.get("weight_g") else "확인 안 됨"),
                ("가격", e(m.get("price") or "확인 안 됨")),
                ("국내 판매", e(KR_SALES[m["kr_sales"]]) + (f" — {e(m['kr_note'])}" if m.get("kr_note") else "")),
                ("블루투스 제조사 ID 식별", ble_cell(m))]
        table = "<div class='tw'><table>" + "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows) + "</table></div>"
        tells = "<ul>" + "".join(f"<li>{e(t)}</li>" for t in m.get("tells") or []) + "</ul>" if m.get("tells") else "<p class='mute'>공개 자료에서 찾지 못함</p>"
        body = f"""<h1>{e(m['name'])} — 시험장 식별 정보</h1>
<p class="lead">카메라 {cam(m)} · 화면 {disp(m)} · 블루투스 제조사 ID {DETECT[m['ble']['detectable']][0]}</p>
{table}
<h2>겉으로 알아보는 법</h2>{tells}
<h2>시험장에서의 의미</h2><p>{e(m.get('exam_risk') or '')}</p>
<h2>출처</h2>{srcs(m['sources'])}
<p class="mute">확인일 2026-11-18 · <a href="{REPO}/blob/main/data/glasses.yaml">원본 yaml</a></p>"""
        desc = f"{m['name']} AI 안경의 카메라·화면·블루투스 제조사 ID·외형 단서. 시험 감독관용 식별 정보."
        urls.append(page(f"/glasses/{m['id']}/", f"{m['name']} 식별 정보 · AI 안경 식별 DB", desc, body,
                         {"@context": "https://schema.org", "@type": "Product", "name": m["name"], "brand": m["maker"], "description": desc}))

    # 홈
    trs = "".join(
        f"<tr><td><a href='/glasses/{m['id']}/'>{e(m['name'])}</a></td><td>{cam(m)}</td><td>{disp(m)}</td>"
        f"<td>{ble_cell(m)}</td><td>{e(KR_SALES[m['kr_sales']])}</td></tr>" for m in glasses)
    nreg = ", ".join(ble["not_registered"])
    body = f"""<h1>AI 스마트안경 식별 데이터베이스</h1>
<p class="lead">시험 감독관과 시험 기관을 위해, 공개 자료로 확인한 AI 안경 {len(glasses)}종의 카메라·화면·블루투스 식별 가능 여부·외형 단서와 국내외 적발 사례를 모았습니다.</p>
<h2>먼저 알아 둘 것</h2>
<ul>
<li><b>블루투스 제조사 ID 로 못 잡는 안경이 있습니다.</b> {e(nreg)} 은 블루투스 SIG 제조사 ID 목록에 업체가 없습니다(2026-11-18 확인). 유튜버 실험으로 화제가 된 Rokid 가 여기에 속합니다. → <a href="/ble-ids/">ID 표</a></li>
<li><b>카메라 없는 화면 안경</b>(Even Realities)은 겉모습이 일반 안경과 거의 같습니다.</li>
<li><b>안경만의 문제가 아닙니다.</b> 제63회 세무사 수석 합격자는 안경 없이 개조한 계산기와 초소형 카메라·모니터를 썼다고 진술했습니다. → <a href="/incidents/">적발 사례</a></li>
<li><b>2027학년도 수능에서 전자기기 부정행위 111건이 적발됐습니다</b>(교육부 2026-11-20 발표). 시험 중 실제 사용은 5건이고 그중 스마트안경은 1건입니다. → <a href="/incidents/">적발 사례</a></li>
<li>한 가지 방법으로는 다 잡지 못합니다. 방법별로 잡는 것과 못 잡는 것을 정리했습니다. → <a href="/methods/">탐지 방법</a></li>
</ul>
<h2>모델별 요약</h2>
<div class="tw"><table><tr><th>모델</th><th>카메라</th><th>화면</th><th>블루투스 ID</th><th>국내</th></tr>{trs}</table></div>
<p class="mute">○ 안경 전용 ID 등록 · △ 폰·이어폰과 ID 공유(오탐 많음) · ✕ SIG 미등록. "등록"은 ID 가 존재한다는 뜻이며 실기기로 잡아 본 결과가 아닙니다.</p>"""
    urls.insert(0, page("/", "AI 스마트안경 식별 DB — 시험 감독관용 카메라·블루투스 ID·적발 사례",
                        "레이밴 메타·Rokid·샤오미 등 AI 안경 13종의 카메라·화면·블루투스 제조사 ID 식별 가능 여부와 국내 시험 적발 사례. 공개 자료 기반, CC BY 4.0.", body,
                        {"@context": "https://schema.org", "@type": "Dataset", "name": "AI 스마트안경 식별 데이터베이스",
                         "description": "시험장 감독관용 AI 안경 식별 정보", "license": "https://creativecommons.org/licenses/by/4.0/",
                         "url": BASE + "/", "dateModified": "2026-11-20"}))

    # 블루투스 ID
    trs = "".join(f"<tr><td><code>{hexid(x['id'])}</code></td><td>{e(x['name'])}</td><td>{'안경·헤드셋 위주' if x['glasses_only'] else '<span class=n>폰·이어폰과 공유</span>'}</td><td>{e(x.get('note') or '')}</td></tr>" for x in ble["ids"])
    body = f"""<h1>스마트안경 업체 블루투스 제조사 ID</h1>
<p class="lead">블루투스 저전력(BLE) 광고 패킷의 제조사 데이터에 실리는 회사 번호입니다. 탐지 앱은 이 번호로 안경을 알아봅니다.</p>
<div class="tw"><table><tr><th>ID</th><th>회사</th><th>구분</th><th>메모</th></tr>{trs}</table></div>
<h2>목록에 없는 업체</h2><ul>{''.join(f'<li>{e(n)}</li>' for n in ble['not_registered'])}</ul>
<p>이 업체 안경은 제조사 ID 방식으로는 식별할 수 없습니다.</p>
<h2>한계</h2><ul><li>ID 가 있다는 것과 기기가 실제로 그 ID 를 광고한다는 것은 다릅니다. 광고를 하지 않는 상태의 기기는 잡히지 않습니다.</li>
<li>이 표는 실기기 측정 결과가 아닙니다.</li></ul>
<h2>출처</h2>{srcs([ble['source']])}<p class="mute">확인일 {e(ble['retrieved'])}</p>"""
    urls.append(page("/ble-ids/", "스마트안경 블루투스 제조사 ID 표 · AI 안경 식별 DB",
                     "메타·룩소티카·Even Realities·스냅 등 스마트안경 업체의 블루투스 SIG 제조사 ID와, 목록에 없는 업체(Rokid·XREAL).", body))

    # 탐지 방법
    secs = ""
    for x in meth:
        tools = "".join(f"<li><a href='{e(t['url'])}'>{e(t['name'])}</a></li>" for t in x.get("tools") or [])
        secs += f"""<h2 id="{x['id']}">{e(x['name'])}</h2>
<div class="tw"><table><tr><th>잡는 것</th><td><ul>{''.join(f'<li>{e(c)}</li>' for c in x['catches'])}</ul></td></tr>
<tr><th>못 잡는 것</th><td><ul>{''.join(f'<li>{e(c)}</li>' for c in x['misses'])}</ul></td></tr>
<tr><th>비용</th><td>{e(x['cost'])}</td></tr>{f'<tr><th>도구</th><td><ul>{tools}</ul></td></tr>' if tools else ''}</table></div>
<p class="mute">출처: {' · '.join(f'<a href="{e(u)}">{i+1}</a>' for i, u in enumerate(x['sources']))}</p>"""
    body = f"""<h1>시험장 AI 부정행위 탐지 방법 비교</h1>
<p class="lead">방법마다 잡는 기기와 놓치는 기기가 다릅니다. 공개 자료 기준이며 성능을 직접 시험한 것은 아닙니다.</p>{secs}"""
    urls.append(page("/methods/", "시험장 AI 안경·카메라 부정행위 탐지 방법 비교 · AI 안경 식별 DB",
                     "육안·블루투스 제조사 ID·코리요스캔 기준선 스캔·전파탐지기·금속탐지·광학 분석·사후 점수 분석이 각각 잡는 것과 못 잡는 것.", body))

    # 적발 사례
    trs = "".join(f"<tr><td>{e(x['date'])}</td><td>{e(x['country'])}</td><td>{e(x['exam'])}</td><td>{ {'glasses':'스마트안경','camera-relay':'초소형 카메라·중계','mixed':'스마트안경·카메라·스마트폰 등'}.get(x['device'], e(x['device'])) }</td><td>{e(x['detected_by'])}</td><td>{e(x['summary'])}<br><span class='mute'>{' · '.join(f'<a href={chr(34)}{e(u)}{chr(34)}>출처{i+1}</a>' for i, u in enumerate(x['sources']))}</span></td></tr>" for x in inc["incidents"])
    stats = "".join(f"<li>{e(s['text'])} (<a href='{e(s['sources'][0])}'>출처</a>)</li>" for s in inc["stats"])
    body = f"""<h1>AI 기기 시험 부정행위 적발 사례</h1>
<p class="lead">공개 보도로 확인한 사례만 적었습니다. 수사 중인 사건은 내용이 바뀔 수 있습니다.</p>
<div class="tw"><table><tr><th>시기</th><th>국가</th><th>시험</th><th>기기</th><th>적발 경위</th><th>내용</th></tr>{trs}</table></div>
<h2>통계</h2><ul>{stats}</ul>"""
    urls.append(page("/incidents/", "AI 안경·AI 커닝 시험 적발 사례 정리(2026) · AI 안경 식별 DB",
                     "수능·토익·국가기술자격·세무사 시험의 AI 안경·초소형 카메라 부정행위 적발 사례와 적발 경위.", body))

    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                     + "".join(f"<url><loc>{u}</loc><lastmod>2026-11-20</lastmod></url>\n" for u in urls) + "</urlset>\n")
    print(f"{len(urls)} pages → {OUT}")


if __name__ == "__main__":
    build()
