#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    KeepTogether,
    LongTable,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

from content_foundation import PACKETS_FOUNDATION
from content_splus import PACKETS_SPLUS
from content_s import PACKETS_S
from content_a import PACKETS_A
from content_exam_updates import apply_exam_updates


ROOT = Path(__file__).resolve().parent
HTML_OUT = ROOT / "docs" / "index.html"
PDF_OUT = ROOT / "docs" / "medical_information_exam_packets_1-46.pdf"
FONT_PATH = ROOT / "tmp" / "pdfs" / "DroidSansFallback.ttf"

AS_OF = "2026年8月18日"
TITLE = "医療情報技師試験 直前対策テキスト"
SUBTITLE = "学習パケット1-46｜優先順位別・弱点集中版"


SOURCES: dict[str, tuple[str, str]] = {
    "S01": ("厚生労働省｜人生の最終段階における医療・ケアの決定プロセス", "https://www.mhlw.go.jp/stf/newpage_02783.html"),
    "S02": ("日本集中治療医学会｜DNAR指示のあり方についての勧告", "https://www.jsicm.org/publication/kankoku_dnar.html"),
    "S03": ("厚生労働省｜医師・看護師等と事務職員等との役割分担", "https://www.mhlw.go.jp/web/t_doc?dataId=00tb3694&dataType=1&pageNo=1"),
    "S04": ("厚生労働省｜医療機関における院内感染対策", "https://www.mhlw.go.jp/web/t_doc?dataId=00tc0640&dataType=1&pageNo=1"),
    "S05": ("厚生労働省｜医療安全対策", "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/iryou/i-anzen/index.html"),
    "S06": ("厚生労働省｜医療事故調査制度", "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000061201.html"),
    "S07": ("日本医療機能評価機構 Mindsガイドラインライブラリ", "https://minds.jcqhc.or.jp/"),
    "S08": ("日本核医学会｜核医学検査", "https://jsnm.org/useful/kensa/"),
    "S09": ("厚生労働省｜2026年度DPC調査 実施説明資料", "https://www.mhlw.go.jp/content/12400000/001738680.pdf"),
    "S10": ("厚生労働省｜DPC/PDPS傷病名コーディングテキスト", "https://www.mhlw.go.jp/content/12400000/001684575.pdf"),
    "S11": ("厚生労働省｜NDBの利用", "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/iryouhoken/reseputo/index.html"),
    "S12": ("National Clinical Database｜NCDについて", "https://www.ncd.or.jp/about/"),
    "S13": ("PMDA｜MID-NET（医療情報データベース）", "https://www.pmda.go.jp/safety/mid-net/0001.html"),
    "S14": ("PMDA｜リアルワールドデータ関連ガイダンス", "https://www.pmda.go.jp/rs-std-jp/standards-development/guidance-guideline/0008.html"),
    "S15": ("厚生労働省｜オンライン資格確認", "https://www.mhlw.go.jp/stf/newpage_08280.html"),
    "S16": ("厚生労働省｜オンライン診療", "https://www.mhlw.go.jp/stf/index_0024_00004.html"),
    "S17": ("厚生労働省｜特定健診・特定保健指導", "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000161103.html"),
    "S18": ("厚生労働省｜電子カルテ情報共有サービス", "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/iryou/johoka/denkarukyouyuu.html"),
    "S19": ("MEDIS-DC｜標準マスター総合サイト", "https://www.medis.or.jp/4_hyojyun/medis-master/index.html"),
    "S20": ("HL7 International｜FHIR Overview", "https://www.hl7.org/fhir/overview.html"),
    "S21": ("HL7 International｜HL7 Version 2 Product Suite", "https://www.hl7.org/implement/standards/product_brief.cfm?product_id=185"),
    "S22": ("DICOM Standard Committee｜DICOM Overview", "https://www.dicomstandard.org/about"),
    "S23": ("IHE International｜Profiles and Standards", "https://www.ihe.net/resources/profiles/"),
    "S24": ("日本医療情報学会｜SS-MIX2仕様書・ガイドライン", "https://www.jami.jp/jamistd/ssmix2/"),
    "S25": ("個人情報保護委員会｜仮名加工情報・匿名加工情報編", "https://www.ppc.go.jp/personalinfo/legal/guidelines_anonymous/"),
    "S26": ("内閣府｜次世代医療基盤法 関係法令・ガイドライン", "https://www8.cao.go.jp/iryou/hourei/hourei.html"),
    "S27": ("厚生労働省｜医療情報システムの安全管理に関するガイドライン第7.0版", "https://www.mhlw.go.jp/stf/shingi/0000516275_00006.html"),
    "S28": ("CDISC｜Operational Data Model（ODM）", "https://www.cdisc.org/standards/data-exchange/odm"),
    "S29": ("厚生労働省｜リスクに基づくモニタリング", "https://www.mhlw.go.jp/web/t_doc?dataId=00tc4393&dataType=1&pageNo=1"),
    "S30": ("厚生労働省｜GCP省令Q&A", "https://www.mhlw.go.jp/web/t_doc?dataId=00tc8624&dataType=1&pageNo=1"),
    "S31": ("ICH｜E6(R3) Good Clinical Practice", "https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Step4_FinalGuideline_2025_0106.pdf"),
    "S32": ("SNIA｜Dictionary（RAID用語）", "https://www.snia.org/sites/default/files/dictionary/SNIADictionary.pdf"),
    "S33": ("LTO Program｜LTO Technology", "https://www.lto.org/what-is-lto/"),
    "S34": ("RFC Editor｜RFC 4632 CIDR", "https://www.rfc-editor.org/info/rfc4632/"),
    "S35": ("Open Networking Foundation｜SDN Definition", "https://opennetworking.org/sdn-definition/"),
    "S36": ("RFC Editor｜RFC 3022 Traditional NAT", "https://www.rfc-editor.org/info/rfc3022/"),
    "S37": ("RFC Editor｜RFC 4511 LDAP", "https://www.rfc-editor.org/info/rfc4511/"),
    "S38": ("Object Management Group｜UML 2.5.1", "https://www.omg.org/spec/UML/2.5.1/About-UML"),
    "S39": ("厚生労働省｜電子的な標準様式 第4期（特定健診）", "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/xml_30799.html"),
    "S40": ("厚生労働省｜医療事故情報収集等事業", "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000020577.html"),
    "S41": ("厚生労働省｜電子処方箋", "https://www.mhlw.go.jp/stf/denshishohousen.html"),
    "S42": ("PMDA｜患者の皆様からの医薬品副作用報告", "https://www.pmda.go.jp/safety/reports/patients/0024.html"),
    "S43": ("厚生労働省｜健康日本21（第三次）", "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/kenkou/kenkounippon21_00006.html"),
    "S44": ("厚生労働省｜救急・災害医療提供体制等の在り方に関する検討会", "https://www.mhlw.go.jp/stf/newpage_07897.html"),
    "S45": ("e-Gov法令検索｜医療法", "https://elaws.e-gov.go.jp/document?lawid=323AC0000000205"),
    "S46": ("厚生労働省｜特定機能病院", "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000137801.html"),
    "S47": ("e-Gov法令検索｜医師法", "https://elaws.e-gov.go.jp/document?lawid=323AC0000000201"),
    "S48": ("LOINC｜About LOINC", "https://loinc.org/about"),
    "S49": ("SNOMED International｜What is SNOMED CT", "https://www.snomed.org/what-is-snomed-ct"),
    "S50": ("厚生労働省｜地域医療支援病院", "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000137801_00015.html"),
    "S51": ("PMDA｜信頼性保証部説明会2026初夏（GCP省令改正・ICH E6(R3)）", "https://www.pmda.go.jp/review-services/symposia/0204.html"),
    "S52": ("厚生労働省｜医療保険", "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/iryouhoken/index.html"),
    "S53": ("厚生労働省｜国民健康保険制度", "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/iryouhoken/koukikourei/index_00002.html"),
    "S54": ("厚生労働省｜高齢者医療制度", "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/iryouhoken/koukikourei/index.html"),
    "S55": ("厚生労働省｜高額療養費制度", "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/kenkou_iryou/iryouhoken/juuyou/kougakuiryou/index.html"),
    "S56": ("厚生労働省｜診療報酬の算定方法", "https://www.mhlw.go.jp/web/t_doc?dataId=84aa9729&dataType=0&pageNo=1"),
    "S57": ("厚生労働省｜令和8年度診療報酬改定", "https://www.mhlw.go.jp/stf/newpage_67729.html"),
    "S58": ("厚生労働省｜令和8年度診療報酬改定説明資料（DPC/PDPS・歯科・調剤）", "https://www.mhlw.go.jp/stf/newpage_71068.html"),
    "S59": ("厚生労働省｜介護保険制度の概要", "https://www.mhlw.go.jp/content/001512842.pdf"),
    "S60": ("厚生労働省｜要介護認定はどのように行われるか", "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/kaigo_koureisha/nintei/gaiyo2.html"),
    "S61": ("e-Gov法令検索｜介護保険法", "https://elaws.e-gov.go.jp/document?lawid=409AC0000000123"),
}


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", text).strip("-")


def html_block(block: dict[str, Any]) -> str:
    kind = block["kind"]
    if kind == "p":
        return f'<p>{block["text"]}</p>'
    if kind == "bullets":
        return "<ul>" + "".join(f"<li>{item}</li>" for item in block["items"]) + "</ul>"
    if kind == "numbered":
        return "<ol>" + "".join(f"<li>{item}</li>" for item in block["items"]) + "</ol>"
    if kind == "flow":
        return '<div class="flow">' + '<span class="arrow">→</span>'.join(
            f"<span>{item}</span>" for item in block["items"]
        ) + "</div>"
    if kind == "note":
        cls = block.get("tone", "info")
        return f'<aside class="note {cls}"><strong>{block["title"]}</strong><p>{block["text"]}</p></aside>'
    if kind == "table":
        head = "".join(f"<th>{h}</th>" for h in block["headers"])
        body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in block["rows"])
        return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'
    raise ValueError(f"Unknown block kind: {kind}")


def build_html(packets: list[dict[str, Any]]) -> None:
    HTML_OUT.parent.mkdir(parents=True, exist_ok=True)
    packet_count = len(packets)

    def progress_heading(title: str, progress_id: str) -> str:
        return (
            '<div class="section-title-row">'
            f'<h3>{escape(title)}</h3>'
            '<label class="read-toggle">'
            f'<input class="read-check" type="checkbox" data-progress-id="{progress_id}">'
            '<span>ここは読んだ</span>'
            '</label></div>'
        )

    toc = []
    packet_html = []
    current_group = None
    part_index = 0
    for packet in packets:
        if packet["group"] != current_group:
            current_group = packet["group"]
            part_index += 1
            toc.append(f'<li class="part-link"><a href="#part-{part_index}">{escape(current_group)}</a></li>')
            packet_html.append(f'<section class="part-divider" id="part-{part_index}"><span>PRIORITY GROUP {part_index}</span><h1>{escape(current_group)}</h1></section>')
        toc.append(
            f'<li class="toc-packet" data-toc-packet="{packet["n"]}">'
            f'<a href="#packet-{packet["n"]}"><b>{packet["n"]}</b> {escape(packet["title"])}'
            '<span class="toc-state" aria-hidden="true">0/0</span></a></li>'
        )
        sections = []
        for i, section in enumerate(packet["sections"], start=1):
            sid = f'p{packet["n"]}-s{i}'
            blocks = "".join(html_block(b) for b in section["blocks"])
            sections.append(
                f'<section class="subsection trackable-section" id="{sid}" data-progress-section="{sid}">'
                f'{progress_heading(section["title"], sid)}{blocks}</section>'
            )
        traps = "".join(
            (
                f'<article class="quiz-item" id="p{packet["n"]}-q{i}" data-quiz-item data-answer="{t["judge"]}">'
                '<div class="quiz-prompt">'
                f'<span class="quiz-number">Q{i}</span><p>{t["claim"]}</p>'
                '</div>'
                f'<div class="quiz-controls" role="group" aria-label="Q{i}の回答">'
                f'<button class="quiz-choice" type="button" data-choice="○" aria-label="正しい、丸" aria-pressed="false" aria-controls="p{packet["n"]}-q{i}-feedback">○</button>'
                f'<button class="quiz-choice" type="button" data-choice="×" aria-label="誤り、バツ" aria-pressed="false" aria-controls="p{packet["n"]}-q{i}-feedback">×</button>'
                '</div>'
                f'<div class="quiz-feedback" id="p{packet["n"]}-q{i}-feedback" hidden aria-live="polite">'
                '<p class="quiz-result"></p>'
                '<div class="quiz-answer-line"><strong>正解</strong>'
                f'<span class="judge {"ok" if t["judge"] == "○" else "ng"}">{t["judge"]}</span></div>'
                f'<p class="quiz-explanation">{t["why"]}</p>'
                '<button class="quiz-retry" type="button">回答をやり直す</button>'
                '</div></article>'
            )
            for i, t in enumerate(packet["traps"], start=1)
        )
        memories = "".join(f"<li>{m}</li>" for m in packet["memory"])
        refs = "".join(
            f'<li><a href="#{sid}">[{sid}] {escape(SOURCES[sid][0])}</a></li>' for sid in packet.get("sources", [])
        )
        goals = "".join(f"<li>{g}</li>" for g in packet["goals"])
        packet_html.append(f'''
        <article class="packet" id="packet-{packet["n"]}">
          <header class="packet-head">
            <div class="packet-no">PACKET {packet["n"]}</div>
            <h2>{escape(packet["title"])}</h2>
            <div class="meta"><span>{escape(packet["field"])}</span><span>目安 {escape(packet["minutes"])}</span><span>{escape(packet["group"])}</span></div>
            <div class="packet-progress" data-packet-progress="{packet["n"]}">0 / 0 セクション</div>
          </header>
          <section class="goal trackable-section" data-progress-section="p{packet["n"]}-goal">{progress_heading("判定目標", f'p{packet["n"]}-goal')}<ul>{goals}</ul></section>
          {''.join(sections)}
          <section class="traps trackable-section" data-progress-section="p{packet["n"]}-traps">{progress_heading("5択で狙われる引っかけ", f'p{packet["n"]}-traps')}
            <p class="quiz-instruction">選択肢の文が正しければ「○」、誤りなら「×」を選択。回答後に正解と解説を表示する。</p>
            <div class="quiz-list">{traps}</div>
          </section>
          <section class="memory trackable-section" data-progress-section="p{packet["n"]}-memory">{progress_heading("試験直前に覚えるセット", f'p{packet["n"]}-memory')}<ol>{memories}</ol></section>
          {f'<section class="packet-sources"><h3>確認した一次資料</h3><ul>{refs}</ul></section>' if refs else ''}
          <a class="back" href="#toc">目次へ戻る</a>
        </article>
        ''')

    refs_html = "".join(
        f'<li id="{sid}"><span>[{sid}]</span> <a href="{escape(url)}">{escape(name)}</a></li>'
        for sid, (name, url) in SOURCES.items()
    )
    css = r'''
    :root{--ink:#18242e;--muted:#5d6a73;--navy:#183a5a;--blue:#146c94;--cyan:#e9f5f8;--line:#d8e0e5;--paper:#fff;--warm:#f7f4ee;--danger:#a63f3f;--ok:#247153}
    *{box-sizing:border-box} html{scroll-behavior:smooth} body{margin:0;color:var(--ink);background:#edf1f3;font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Yu Gothic",Meiryo,sans-serif;line-height:1.72;font-size:15px}
    a{color:#0b628b;text-decoration:none} a:hover{text-decoration:underline}
    .screen-nav{position:fixed;left:0;top:0;bottom:0;width:292px;overflow:auto;background:#102d45;color:#e8f0f4;padding:25px 19px;z-index:4}.screen-nav h2{font-size:15px;margin:0 0 14px;color:#fff}.screen-nav ol{list-style:none;padding:0;margin:0}.screen-nav li a{display:block;color:#cde0ea;padding:4px 7px;border-radius:5px;font-size:12.5px}.screen-nav li a:hover{background:#1d4563;text-decoration:none;color:#fff}.screen-nav .part-link a{color:#fff;font-weight:700;margin-top:10px;border-top:1px solid #365971;padding-top:10px}.screen-nav .toc-state{float:right;color:#8fb5c5;font-size:10px;margin-left:5px}.screen-nav .toc-packet.is-complete a{color:#aee3c8}.screen-nav .toc-packet.is-complete .toc-state{color:#78d5a5}.nav-progress{padding:11px 10px;margin:0 0 13px;border:1px solid #365971;border-radius:8px;background:#ffffff0b}.nav-progress strong{display:block;font-size:12px;color:#fff;margin-bottom:7px}.nav-meter{height:5px;overflow:hidden;border-radius:99px;background:#31536b}.nav-meter span{display:block;width:0;height:100%;background:#63c493;transition:width .2s ease}
    main{max-width:980px;margin:0 auto 0 calc(292px + max(22px,(100vw - 1272px)/2));background:var(--paper);min-height:100vh;box-shadow:0 0 30px #b5c0c6;padding:0 70px 90px}
    .cover{min-height:100vh;margin:0 -70px;padding:95px 80px 70px;background:linear-gradient(145deg,#102d45 0%,#1b4e6d 62%,#2f8197 100%);color:white;display:flex;flex-direction:column;justify-content:space-between}.cover .kicker{letter-spacing:.16em;font-size:13px}.cover h1{font-size:44px;line-height:1.2;margin:18px 0 8px}.cover h2{font-weight:500;font-size:24px;margin:0;color:#d8edf4}.cover .cover-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:50px}.cover .cover-grid div{border:1px solid #78a7b9;background:#ffffff12;padding:14px 17px;border-radius:8px}.cover small{color:#d3e4eb}
    .front{padding:65px 0}.front h2{font-size:28px;color:var(--navy);border-bottom:3px solid #2b809a;padding-bottom:10px}.front .scope{display:grid;grid-template-columns:repeat(3,1fr);gap:13px}.scope div{background:var(--cyan);border-left:5px solid #2b809a;padding:15px}.scope b{display:block;font-size:20px;color:var(--navy)}
    .progress-dashboard{margin:15px 0 55px;padding:24px;border:1px solid #c7d8df;border-radius:12px;background:#f4f8f9}.progress-dashboard h2{margin:0 0 16px;font-size:25px;color:var(--navy)}.progress-summary{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.progress-summary div{padding:13px 15px;border-radius:8px;background:#fff;border:1px solid var(--line)}.progress-summary strong{display:block;color:var(--navy);font-size:21px;line-height:1.25}.progress-summary span{font-size:12px;color:var(--muted)}.progress-meter{height:10px;margin:15px 0 17px;border-radius:99px;overflow:hidden;background:#dbe5e9}.progress-meter span{display:block;width:0;height:100%;background:var(--ok);transition:width .2s ease}.progress-actions{display:flex;flex-wrap:wrap;gap:8px}.progress-button{appearance:none;border:1px solid #9fb5bf;border-radius:7px;background:#fff;color:#214457;padding:9px 12px;font:inherit;font-size:13px;font-weight:650;cursor:pointer}.progress-button:hover{background:#eaf3f5}.progress-button.primary{background:#1d6684;color:#fff;border-color:#1d6684}.progress-button.danger{color:#943f3f;border-color:#d7b2b2}.progress-file-input{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}.storage-status{margin:12px 0 0;font-size:12px;color:var(--muted)}.storage-status[data-tone="error"]{color:#943f3f}
    .print-toc{columns:2;column-gap:38px;list-style:none;padding-left:0}.print-toc li{break-inside:avoid;margin:4px 0}.print-toc .part-link{margin-top:13px;border-bottom:1px solid var(--line);font-weight:700}.print-toc b{display:inline-block;width:25px;color:var(--blue)}
    .part-divider{min-height:62vh;margin:40px -70px 0;padding:140px 75px 80px;background:#163950;color:white;display:flex;flex-direction:column;justify-content:center}.part-divider span{letter-spacing:.2em;color:#aad1df}.part-divider h1{font-size:40px;margin:8px 0}
    .packet{padding:68px 0 30px;scroll-margin-top:20px}.packet+.packet{border-top:1px solid var(--line)}.packet-head{border-left:8px solid #2a7e98;padding:0 0 0 18px;margin-bottom:26px}.packet.is-complete .packet-head{border-left-color:var(--ok)}.packet-no{letter-spacing:.1em;color:var(--blue);font-weight:700;font-size:12px}.packet h2{font-size:31px;line-height:1.3;margin:5px 0;color:var(--navy)}.meta{display:flex;flex-wrap:wrap;gap:8px}.meta span{font-size:12px;padding:2px 8px;border-radius:999px;background:#eaf1f4;color:#3b5969}.packet-progress{display:inline-block;margin-top:9px;padding:3px 9px;border-radius:999px;background:#edf3f5;color:#48616e;font-size:12px;font-weight:650}.packet.is-complete .packet-progress{background:#e1f3e9;color:#226343}
    h3{font-size:19px;color:var(--navy);margin:30px 0 10px}.section-title-row{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}.section-title-row h3{flex:1}.read-toggle{display:inline-flex;align-items:center;gap:7px;flex:0 0 auto;margin-top:27px;padding:5px 9px;border:1px solid #b7c9d1;border-radius:999px;background:#fff;color:#48616e;font-size:12px;font-weight:650;line-height:1.35;cursor:pointer;user-select:none}.read-toggle input{width:18px;height:18px;margin:0;accent-color:var(--ok)}.trackable-section{transition:background-color .15s ease,box-shadow .15s ease}.trackable-section.is-read{box-shadow:inset 4px 0 var(--ok);background-color:#f2faf5}.trackable-section.is-read .read-toggle{border-color:#86bca0;background:#e1f3e9;color:#205f41}.goal{background:#eef8fa;border:1px solid #c7e1e7;border-radius:8px;padding:5px 20px 12px}.goal.is-read{background:#edf8f1}.goal .section-title-row h3{margin:12px 0 3px}.goal .read-toggle{margin-top:10px}.goal ul{margin:5px 0}.subsection{padding:1px 12px 12px;margin:0 -12px;border-radius:7px}.subsection>p:first-of-type{margin-top:5px}.flow{display:flex;align-items:stretch;flex-wrap:wrap;gap:5px;margin:15px 0}.flow span:not(.arrow){padding:7px 10px;background:#edf4f6;border:1px solid #d1e1e6;border-radius:5px;font-weight:600}.flow .arrow{padding:6px 0;color:#438199;font-weight:700}
    .note{margin:15px 0;padding:12px 16px;border-left:5px solid #347f99;background:#f0f6f8}.note p{margin:3px 0}.note.warn{border-color:#b77a31;background:#fff8ec}.note.danger{border-color:#b04a4a;background:#fff3f1}
    .table-wrap{overflow:auto;margin:14px 0}table{border-collapse:collapse;width:100%;font-size:13px;line-height:1.52}th{background:#183f5a;color:white;text-align:left;padding:8px;border:1px solid #264f69}td{vertical-align:top;padding:8px;border:1px solid var(--line)}tbody tr:nth-child(even){background:#f7f9fa}.judge{display:inline-grid;place-items:center;width:27px;height:27px;border-radius:50%;font-weight:800;color:#fff}.judge.ok{background:var(--ok)}.judge.ng{background:var(--danger)}
    .quiz-instruction{margin:3px 0 14px;color:var(--muted);font-size:13px}.quiz-list{display:grid;gap:12px}.quiz-item{padding:15px 16px;border:1px solid #cedae0;border-radius:9px;background:#fff;transition:border-color .15s ease,background-color .15s ease}.quiz-item.answered.correct{border-color:#8dc1a6;background:#f2faf5}.quiz-item.answered.incorrect{border-color:#d7a3a3;background:#fff7f6}.quiz-prompt{display:flex;align-items:flex-start;gap:10px}.quiz-prompt p{margin:0;font-weight:650}.quiz-number{flex:0 0 auto;display:inline-grid;place-items:center;min-width:31px;height:27px;padding:0 6px;border-radius:5px;background:#e8f1f5;color:#215673;font-size:12px;font-weight:800}.quiz-controls{display:flex;gap:10px;margin:13px 0 0 41px}.quiz-choice{appearance:none;min-width:76px;min-height:44px;border:2px solid #9eb5c0;border-radius:8px;background:#fff;color:#244a5c;font:inherit;font-size:23px;font-weight:800;line-height:1;cursor:pointer}.quiz-choice:hover{border-color:#317997;background:#eef7fa}.quiz-choice:focus-visible,.quiz-retry:focus-visible{outline:3px solid #75abc0;outline-offset:2px}.quiz-choice[disabled]{cursor:default;opacity:.58}.quiz-choice.is-selected{opacity:1}.quiz-item.correct .quiz-choice.is-selected{border-color:var(--ok);background:#e0f2e8;color:#1f6545}.quiz-item.incorrect .quiz-choice.is-selected{border-color:var(--danger);background:#f8e2e0;color:#8f3535}.quiz-feedback{margin:14px 0 0 41px;padding:12px 14px;border-left:5px solid #879ba5;background:#f5f8f9}.quiz-item.correct .quiz-feedback{border-left-color:var(--ok);background:#e9f6ee}.quiz-item.incorrect .quiz-feedback{border-left-color:var(--danger);background:#fcebea}.quiz-result{margin:0 0 8px;font-weight:800}.quiz-result.correct{color:#1f6545}.quiz-result.incorrect{color:#923b3b}.quiz-answer-line{display:flex;align-items:center;gap:9px;margin-bottom:5px}.quiz-answer-line .judge{width:24px;height:24px;font-size:13px}.quiz-explanation{margin:5px 0}.quiz-retry{appearance:none;margin-top:7px;padding:6px 10px;border:1px solid #a7b9c1;border-radius:6px;background:#fff;color:#365766;font:inherit;font-size:12px;font-weight:650;cursor:pointer}.quiz-retry:hover{background:#eef3f5}
    .memory{background:var(--warm);border-top:3px solid #b59561;border-bottom:1px solid #dfd3bf;padding:4px 20px 10px;margin-top:28px}.memory.is-read{background:#edf8f1}.memory .section-title-row h3{margin-top:12px}.memory .read-toggle{margin-top:10px}.memory li{margin:5px 0;font-weight:600}.traps{padding:1px 12px 12px;margin:0 -12px;border-radius:7px}.packet-sources{font-size:12px;color:var(--muted)}.packet-sources h3{font-size:14px}.back{display:inline-block;margin-top:18px;font-size:12px}.references li{margin:8px 0}.references li span{font-family:monospace;color:#4d6572}
    @media(max-width:950px){.screen-nav{display:none}main{margin:0 auto;padding:0 24px}.cover,.part-divider{margin-left:-24px;margin-right:-24px;padding-left:32px;padding-right:32px}.cover h1{font-size:34px}.cover .cover-grid,.front .scope,.progress-summary{grid-template-columns:1fr}.print-toc{columns:1}.progress-dashboard{padding:18px;margin-bottom:35px}.progress-actions{display:grid;grid-template-columns:1fr 1fr}.progress-button{text-align:center}.section-title-row{align-items:center;gap:9px}.section-title-row h3{font-size:18px}.read-toggle{margin-top:22px}.goal .read-toggle,.memory .read-toggle{margin-top:8px}.read-toggle span{white-space:nowrap}}
    @media(max-width:520px){.progress-actions{grid-template-columns:1fr}.read-toggle{padding:5px 7px;font-size:11px}.read-toggle input{width:20px;height:20px}.quiz-item{padding:13px 12px}.quiz-controls,.quiz-feedback{margin-left:0}.quiz-choice{flex:1;min-width:0}}
    @media print{@page{size:A4;margin:16mm 15mm 17mm;@bottom-center{content:"医療情報技師試験 直前対策｜" counter(page);font-size:8pt;color:#63727c}}body{background:white;font-size:9.2pt;line-height:1.58}.screen-nav,.progress-dashboard,.read-toggle,.packet-progress,.toc-state{display:none!important}main{max-width:none;margin:0;padding:0;box-shadow:none}.cover{min-height:255mm;margin:-16mm -15mm -17mm;padding:33mm 21mm 24mm;page-break-after:always}.cover h1{font-size:31pt}.cover h2{font-size:17pt}.front{padding:0;page-break-after:always}.front h2{font-size:19pt}.part-divider{min-height:255mm;margin:-16mm -15mm -17mm;padding:40mm 20mm;page-break-before:always;page-break-after:always}.part-divider h1{font-size:27pt}.packet{padding:0;page-break-before:always}.packet+.packet{border-top:0}.packet h2{font-size:21pt}.packet-head{margin-bottom:6mm}h3{font-size:13pt;margin-top:6mm}.trackable-section,.trackable-section.is-read{box-shadow:none;background-color:transparent}.goal,.goal.is-read,.memory,.memory.is-read,.note{break-inside:avoid}.goal,.goal.is-read{background:#eef8fa}.memory,.memory.is-read{background:var(--warm)}.table-wrap{overflow:visible}table{font-size:7.8pt}tr{break-inside:avoid}.quiz-instruction,.quiz-controls,.quiz-result,.quiz-retry{display:none!important}.quiz-list{display:block}.quiz-item{break-inside:avoid;margin:0 0 3mm;padding:3mm;border-radius:0}.quiz-feedback[hidden],.quiz-feedback{display:block!important;margin:2mm 0 0;padding:2mm 3mm}.back{display:none}.print-toc{columns:2}}
    '''
    js = r'''
    (() => {
      'use strict';
      const STORAGE_KEY = 'medical-information-exam-packets-4-46-progress-v1';
      const DOC_ID = 'medical-information-exam-packets-4-46';
      const boxes = Array.from(document.querySelectorAll('.read-check[data-progress-id]'));
      const knownIds = new Set(boxes.map((box) => box.dataset.progressId));
      const packets = Array.from(document.querySelectorAll('.packet'));
      const quizItems = Array.from(document.querySelectorAll('[data-quiz-item]'));
      const storageStatus = document.getElementById('storage-status');
      const lastUpdated = document.getElementById('last-updated');
      let storageAvailable = false;

      function emptyState() {
        return { version: 1, docId: DOC_ID, checked: [], updatedAt: '' };
      }

      function normalizeState(payload) {
        if (!payload || typeof payload !== 'object') return emptyState();
        let checked = [];
        if (Array.isArray(payload.checked)) {
          checked = payload.checked;
        } else if (payload.checked && typeof payload.checked === 'object') {
          checked = Object.keys(payload.checked).filter((key) => payload.checked[key]);
        }
        return {
          version: 1,
          docId: DOC_ID,
          checked: Array.from(new Set(checked.filter((id) => knownIds.has(id)))),
          updatedAt: typeof payload.updatedAt === 'string' ? payload.updatedAt : ''
        };
      }

      function readEmbeddedState() {
        const node = document.getElementById('embedded-progress');
        if (!node) return emptyState();
        try {
          return normalizeState(JSON.parse(node.textContent || '{}'));
        } catch (_) {
          return emptyState();
        }
      }

      function readLocalState() {
        try {
          const probe = STORAGE_KEY + '-probe';
          localStorage.setItem(probe, '1');
          localStorage.removeItem(probe);
          storageAvailable = true;
        } catch (_) {
          storageAvailable = false;
          return emptyState();
        }
        try {
          return normalizeState(JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'));
        } catch (_) {
          return emptyState();
        }
      }

      function newerState(a, b) {
        const aTime = Date.parse(a.updatedAt || '') || 0;
        const bTime = Date.parse(b.updatedAt || '') || 0;
        return bTime > aTime ? b : a;
      }

      function snapshot() {
        return {
          version: 1,
          docId: DOC_ID,
          checked: boxes.filter((box) => box.checked).map((box) => box.dataset.progressId),
          updatedAt: new Date().toISOString()
        };
      }

      function setStatus(message, tone = '') {
        if (!storageStatus) return;
        storageStatus.textContent = message;
        storageStatus.dataset.tone = tone;
      }

      function updateUi(updatedAt = '') {
        boxes.forEach((box) => {
          const section = box.closest('.trackable-section');
          if (section) section.classList.toggle('is-read', box.checked);
        });

        let completedPackets = 0;
        packets.forEach((packet) => {
          const packetBoxes = Array.from(packet.querySelectorAll('.read-check[data-progress-id]'));
          const done = packetBoxes.filter((box) => box.checked).length;
          const total = packetBoxes.length;
          const complete = total > 0 && done === total;
          const packetNo = packet.id.replace('packet-', '');
          packet.classList.toggle('is-complete', complete);
          const label = packet.querySelector('[data-packet-progress]');
          if (label) label.textContent = complete ? `全 ${total} セクション読了` : `${done} / ${total} セクション`;
          document.querySelectorAll(`[data-toc-packet="${packetNo}"]`).forEach((item) => {
            item.classList.toggle('is-complete', complete);
            const state = item.querySelector('.toc-state');
            if (state) state.textContent = `${done}/${total}`;
          });
          if (complete) completedPackets += 1;
        });

        const completedSections = boxes.filter((box) => box.checked).length;
        const percent = boxes.length ? Math.round(completedSections / boxes.length * 100) : 0;
        const sectionCounter = document.getElementById('section-counter');
        const packetCounter = document.getElementById('packet-counter');
        const percentCounter = document.getElementById('percent-counter');
        const progressFill = document.getElementById('progress-fill');
        const navPacketProgress = document.getElementById('nav-packet-progress');
        const navProgressFill = document.getElementById('nav-progress-fill');
        if (sectionCounter) sectionCounter.textContent = `${completedSections} / ${boxes.length}`;
        if (packetCounter) packetCounter.textContent = `${completedPackets} / ${packets.length}`;
        if (percentCounter) percentCounter.textContent = `${percent}%`;
        if (progressFill) {
          progressFill.style.width = `${percent}%`;
          progressFill.parentElement.setAttribute('aria-valuenow', String(percent));
        }
        if (navPacketProgress) navPacketProgress.textContent = `${completedPackets} / ${packets.length} パケット読了`;
        if (navProgressFill) navProgressFill.style.width = `${percent}%`;
        if (lastUpdated) {
          const parsed = Date.parse(updatedAt || '');
          lastUpdated.textContent = parsed ? new Date(parsed).toLocaleString('ja-JP') : '未保存';
        }
      }

      function persist() {
        const state = snapshot();
        updateUi(state.updatedAt);
        if (!storageAvailable) {
          setStatus('端末内への自動保存は利用できません。進捗入りHTMLまたはJSONを書き出してください。', 'error');
          return state;
        }
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
          setStatus('チェック内容を端末内へ自動保存しました。');
        } catch (_) {
          storageAvailable = false;
          setStatus('端末内への自動保存に失敗しました。進捗入りHTMLまたはJSONを書き出してください。', 'error');
        }
        return state;
      }

      function applyState(payload, saveAfter = false) {
        const state = normalizeState(payload);
        const selected = new Set(state.checked);
        boxes.forEach((box) => { box.checked = selected.has(box.dataset.progressId); });
        updateUi(state.updatedAt);
        if (saveAfter) return persist();
        return state;
      }

      function downloadFile(contents, filename, mimeType) {
        const blob = new Blob([contents], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1500);
      }

      function resetQuizItem(item, focusFirst = false) {
        item.classList.remove('answered', 'correct', 'incorrect');
        const feedback = item.querySelector('.quiz-feedback');
        const result = item.querySelector('.quiz-result');
        const choices = Array.from(item.querySelectorAll('.quiz-choice[data-choice]'));
        if (feedback) feedback.hidden = true;
        if (result) {
          result.textContent = '';
          result.className = 'quiz-result';
        }
        choices.forEach((choice) => {
          choice.disabled = false;
          choice.classList.remove('is-selected');
          choice.setAttribute('aria-pressed', 'false');
        });
        if (focusFirst && choices[0]) choices[0].focus();
      }

      function answerQuizItem(item, selected) {
        const answer = item.dataset.answer;
        const isCorrect = selected === answer;
        const feedback = item.querySelector('.quiz-feedback');
        const result = item.querySelector('.quiz-result');
        item.classList.remove('correct', 'incorrect');
        item.classList.add('answered', isCorrect ? 'correct' : 'incorrect');
        item.querySelectorAll('.quiz-choice[data-choice]').forEach((choice) => {
          const chosen = choice.dataset.choice === selected;
          choice.disabled = true;
          choice.classList.toggle('is-selected', chosen);
          choice.setAttribute('aria-pressed', chosen ? 'true' : 'false');
        });
        if (result) {
          result.textContent = isCorrect ? '正解' : '不正解';
          result.className = `quiz-result ${isCorrect ? 'correct' : 'incorrect'}`;
        }
        if (feedback) feedback.hidden = false;
      }

      const initialState = newerState(readEmbeddedState(), readLocalState());
      applyState(initialState);
      if (storageAvailable) {
        setStatus('チェック内容は変更のたびに端末内へ自動保存されます。');
        if (initialState.updatedAt) localStorage.setItem(STORAGE_KEY, JSON.stringify(initialState));
      } else {
        setStatus('この表示環境では端末内への自動保存を利用できません。', 'error');
      }

      boxes.forEach((box) => box.addEventListener('change', persist));

      quizItems.forEach((item) => {
        item.querySelectorAll('.quiz-choice[data-choice]').forEach((choice) => {
          choice.addEventListener('click', () => answerQuizItem(item, choice.dataset.choice));
        });
        const retry = item.querySelector('.quiz-retry');
        if (retry) retry.addEventListener('click', () => resetQuizItem(item, true));
      });

      const exportJson = document.getElementById('export-progress');
      if (exportJson) exportJson.addEventListener('click', () => {
        const state = persist();
        const date = state.updatedAt.slice(0, 10) || 'progress';
        downloadFile(JSON.stringify(state, null, 2), `medical_information_progress_${date}.json`, 'application/json;charset=utf-8');
      });

      const exportHtml = document.getElementById('export-html');
      if (exportHtml) exportHtml.addEventListener('click', () => {
        const state = persist();
        const clone = document.documentElement.cloneNode(true);
        const selected = new Set(state.checked);
        clone.querySelectorAll('.read-check[data-progress-id]').forEach((box) => {
          const checked = selected.has(box.dataset.progressId);
          box.checked = checked;
          if (checked) box.setAttribute('checked', '');
          else box.removeAttribute('checked');
        });
        clone.querySelectorAll('[data-quiz-item]').forEach((item) => {
          item.classList.remove('answered', 'correct', 'incorrect');
          const feedback = item.querySelector('.quiz-feedback');
          const result = item.querySelector('.quiz-result');
          if (feedback) feedback.setAttribute('hidden', '');
          if (result) {
            result.textContent = '';
            result.className = 'quiz-result';
          }
          item.querySelectorAll('.quiz-choice[data-choice]').forEach((choice) => {
            choice.disabled = false;
            choice.removeAttribute('disabled');
            choice.classList.remove('is-selected');
            choice.setAttribute('aria-pressed', 'false');
          });
        });
        const embedded = clone.querySelector('#embedded-progress');
        if (embedded) embedded.textContent = JSON.stringify(state).replace(/</g, '\\u003c');
        const date = state.updatedAt.slice(0, 10) || 'progress';
        downloadFile('<!doctype html>\n' + clone.outerHTML, `medical_information_exam_packets_1-46_progress_${date}.html`, 'text/html;charset=utf-8');
        setStatus('現在のチェック状態を埋め込んだHTMLを作成しました。');
      });

      const importInput = document.getElementById('import-progress');
      if (importInput) importInput.addEventListener('change', () => {
        const file = importInput.files && importInput.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = () => {
          try {
            const payload = JSON.parse(String(reader.result || '{}'));
            if (payload.docId && payload.docId !== DOC_ID) throw new Error('document mismatch');
            applyState(payload, true);
            setStatus('進捗JSONを読み込み、チェック状態を反映しました。');
          } catch (_) {
            setStatus('進捗JSONを読み込めませんでした。ファイル内容を確認してください。', 'error');
          }
          importInput.value = '';
        };
        reader.onerror = () => {
          setStatus('進捗JSONの読み込みに失敗しました。', 'error');
          importInput.value = '';
        };
        reader.readAsText(file);
      });

      const resetButton = document.getElementById('reset-progress');
      if (resetButton) resetButton.addEventListener('click', () => {
        if (!window.confirm('すべてのチェックを外しますか？')) return;
        boxes.forEach((box) => { box.checked = false; });
        persist();
        setStatus('すべてのチェックを外しました。');
      });
    })();
    '''
    embedded_progress = '{"version":1,"docId":"medical-information-exam-packets-4-46","checked":[],"updatedAt":""}'
    html = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{TITLE}</title><style>{css}</style></head><body>
    <nav class="screen-nav"><h2>{TITLE}</h2><div class="nav-progress"><strong id="nav-packet-progress">0 / {packet_count} パケット読了</strong><div class="nav-meter" aria-hidden="true"><span id="nav-progress-fill"></span></div></div><ol>{''.join(toc)}</ol></nav>
    <main>
      <section class="cover"><div><div class="kicker">2026 EXAM / RAPID REVIEW</div><h1>{TITLE}</h1><h2>{SUBTITLE}</h2><div class="cover-grid"><div><b>対象</b><br>学習パケット1-46</div><div><b>設計</b><br>20-40分 × {packet_count}パケット</div><div><b>重点</b><br>境界・業務フロー・規格の用途</div><div><b>確認基準日</b><br>{AS_OF}</div></div></div><small>第8版3冊と過去問誤答傾向に基づく個人学習用教材</small></section>
      <section class="front"><h2>使い方と収録範囲</h2><p>更新版リストの学習パケット1から46を、判定目標 → 概念と比較 → 現場フロー → 引っかけ → 直前暗記の順で収録した。パケット1～3は、既習事項の再確認と5択演習に使えるよう、制度の主体・給付・請求・認定フローまで整理している。</p><div class="scope"><div><b>S+ 1-18</b>最優先・18パケット</div><div><b>S 19-36</b>重点・18パケット</div><div><b>A 37-46</b>補強・10パケット</div></div><h3>制度情報の扱い</h3><p>制度・法令・ガイドラインは{AS_OF}時点の一次資料を確認した。令和8年度診療報酬改定、安全管理ガイドライン第7.0版、オンライン診療指針の2026年4月一部改訂を基準とする。診療報酬の細かな点数や施設基準は出題判定に必要な範囲だけを扱う。</p><aside class="note warn"><strong>試験年度とのずれ</strong><p>第8版教材や作問時点が現行制度より前の場合、版番号そのものより、本人同意・最小権限・標準規格の用途など改定後も維持される原則を優先する。</p></aside></section>
      <section class="progress-dashboard" id="progress"><h2>学習進捗</h2><div class="progress-summary"><div><strong id="section-counter">0 / 0</strong><span>読了セクション</span></div><div><strong id="packet-counter">0 / {packet_count}</strong><span>全セクション読了パケット</span></div><div><strong id="percent-counter">0%</strong><span>全体進捗</span></div></div><div class="progress-meter" role="progressbar" aria-label="全体進捗" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span id="progress-fill"></span></div><div class="progress-actions"><button class="progress-button primary" id="export-html" type="button">進捗入りHTMLを保存</button><button class="progress-button" id="export-progress" type="button">進捗JSONを書き出す</button><label class="progress-button" for="import-progress">進捗JSONを読み込む</label><input class="progress-file-input" id="import-progress" type="file" accept="application/json,.json"><button class="progress-button danger" id="reset-progress" type="button">進捗をリセット</button></div><p class="storage-status" id="storage-status">保存機能を確認しています。</p><p class="storage-status">最終更新：<span id="last-updated">未保存</span>。HTML自体は自動上書きされません。端末外へ移す場合は「進捗入りHTMLを保存」または進捗JSONを使用してください。</p></section>
      <section class="front" id="toc"><h2>目次</h2><ul class="print-toc">{''.join(toc)}</ul></section>
      {''.join(packet_html)}
      <section class="front references" id="references"><h2>一次資料一覧</h2><ol>{refs_html}</ol><p>URLおよび現行版は{AS_OF}に確認。本文は試験対策用の要約であり、原資料の全文を代替しない。</p></section>
    </main><script id="embedded-progress" type="application/json">{embedded_progress}</script><script>{js}</script></body></html>'''
    HTML_OUT.write_text(html, encoding="utf-8")


@dataclass
class PDFTheme:
    ink: colors.Color = colors.HexColor("#18242E")
    navy: colors.Color = colors.HexColor("#183A5A")
    blue: colors.Color = colors.HexColor("#146C94")
    cyan: colors.Color = colors.HexColor("#E9F5F8")
    line: colors.Color = colors.HexColor("#D8E0E5")
    warm: colors.Color = colors.HexColor("#F7F4EE")
    red: colors.Color = colors.HexColor("#A63F3F")
    green: colors.Color = colors.HexColor("#247153")


class GuideDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str, styles: dict[str, ParagraphStyle]):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=17 * mm,
            rightMargin=17 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            title=TITLE,
            author="OpenAI Codex",
            subject="2026年度 医療情報技師試験 直前対策",
        )
        self.guide_styles = styles
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="normal")
        self.addPageTemplates([
            PageTemplate(id="main", frames=[frame], onPage=self._header_footer),
        ])

    def _header_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("HeiseiKakuGo-W5", 7.5)
        canvas.setFillColor(colors.HexColor("#667680"))
        if doc.page > 1:
            canvas.drawString(self.leftMargin, A4[1] - 10 * mm, "医療情報技師試験 直前対策｜学習パケット1-46")
        canvas.drawCentredString(A4[0] / 2, 9 * mm, str(doc.page))
        canvas.restoreState()

    def afterFlowable(self, flowable):
        style_name = getattr(getattr(flowable, "style", None), "name", "")
        if style_name not in {"PartTitle", "PacketTitle"}:
            return
        text = strip_tags(flowable.getPlainText())
        level = 0 if style_name == "PartTitle" else 1
        key = getattr(flowable, "_bookmark_key", f"h-{self.page}-{slug(text)}")
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=level, closed=(level == 0))
        self.notify("TOCEntry", (level, text, self.page, key))


def pdf_styles() -> dict[str, ParagraphStyle]:
    if not FONT_PATH.exists():
        import fitz

        FONT_PATH.parent.mkdir(parents=True, exist_ok=True)
        FONT_PATH.write_bytes(fitz.Font(fontname="japan-s").buffer)
    pdfmetrics.registerFont(TTFont("HeiseiKakuGo-W5", str(FONT_PATH)))
    pdfmetrics.registerFont(TTFont("HeiseiMin-W3", str(FONT_PATH)))
    pdfmetrics.registerFontFamily("HeiseiKakuGo-W5", normal="HeiseiKakuGo-W5", bold="HeiseiKakuGo-W5", italic="HeiseiKakuGo-W5", boldItalic="HeiseiKakuGo-W5")
    pdfmetrics.registerFontFamily("HeiseiMin-W3", normal="HeiseiMin-W3", bold="HeiseiMin-W3", italic="HeiseiMin-W3", boldItalic="HeiseiMin-W3")
    t = PDFTheme()
    base = getSampleStyleSheet()
    return {
        "CoverKicker": ParagraphStyle("CoverKicker", fontName="HeiseiKakuGo-W5", fontSize=10, leading=14, textColor=colors.HexColor("#B9DCE7"), spaceAfter=12),
        "CoverTitle": ParagraphStyle("CoverTitle", fontName="HeiseiKakuGo-W5", fontSize=27, leading=35, textColor=colors.white, spaceAfter=10),
        "CoverSub": ParagraphStyle("CoverSub", fontName="HeiseiKakuGo-W5", fontSize=16, leading=22, textColor=colors.HexColor("#D8EDF4"), spaceAfter=25),
        "FrontTitle": ParagraphStyle("FrontTitle", fontName="HeiseiKakuGo-W5", fontSize=20, leading=26, textColor=t.navy, spaceAfter=11, borderWidth=0, borderPadding=0),
        "Body": ParagraphStyle("Body", fontName="HeiseiMin-W3", fontSize=9.25, leading=15.0, textColor=t.ink, spaceAfter=6, wordWrap="CJK"),
        "BodySmall": ParagraphStyle("BodySmall", fontName="HeiseiMin-W3", fontSize=7.7, leading=11.2, textColor=t.ink, wordWrap="CJK"),
        "BodyTiny": ParagraphStyle("BodyTiny", fontName="HeiseiMin-W3", fontSize=6.8, leading=9.4, textColor=t.ink, wordWrap="CJK"),
        "PartTitle": ParagraphStyle("PartTitle", fontName="HeiseiKakuGo-W5", fontSize=26, leading=34, textColor=colors.white, backColor=t.navy, borderPadding=24, alignment=TA_CENTER, spaceAfter=12),
        "PartNo": ParagraphStyle("PartNo", fontName="HeiseiKakuGo-W5", fontSize=10, leading=14, textColor=colors.HexColor("#B9DCE7"), alignment=TA_CENTER, spaceAfter=8),
        "PacketTitle": ParagraphStyle("PacketTitle", fontName="HeiseiKakuGo-W5", fontSize=20, leading=26, textColor=t.navy, spaceAfter=5, borderColor=t.blue, borderWidth=0, leftIndent=0),
        "PacketMeta": ParagraphStyle("PacketMeta", fontName="HeiseiKakuGo-W5", fontSize=7.8, leading=11, textColor=colors.HexColor("#4D6674"), spaceAfter=10),
        "SubTitle": ParagraphStyle("SubTitle", fontName="HeiseiKakuGo-W5", fontSize=12.5, leading=17, textColor=t.navy, spaceBefore=10, spaceAfter=5, keepWithNext=True),
        "BoxTitle": ParagraphStyle("BoxTitle", fontName="HeiseiKakuGo-W5", fontSize=10.2, leading=14, textColor=t.navy, spaceAfter=4),
        "Bullet": ParagraphStyle("Bullet", parent=base["BodyText"], fontName="HeiseiMin-W3", fontSize=9, leading=14.5, leftIndent=12, firstLineIndent=-8, bulletIndent=2, textColor=t.ink, spaceAfter=2, wordWrap="CJK"),
        "Number": ParagraphStyle("Number", parent=base["BodyText"], fontName="HeiseiMin-W3", fontSize=9, leading=14.5, leftIndent=14, firstLineIndent=-10, textColor=t.ink, spaceAfter=3, wordWrap="CJK"),
        "Source": ParagraphStyle("Source", fontName="HeiseiMin-W3", fontSize=7.2, leading=10.5, textColor=colors.HexColor("#586A75"), leftIndent=10, firstLineIndent=-8, wordWrap="CJK"),
        "TOC0": ParagraphStyle("TOC0", fontName="HeiseiKakuGo-W5", fontSize=11, leading=16, leftIndent=0, textColor=t.navy, spaceBefore=7),
        "TOC1": ParagraphStyle("TOC1", fontName="HeiseiMin-W3", fontSize=8.5, leading=12.5, leftIndent=12, firstLineIndent=-8, textColor=t.ink),
    }


def styled_table(headers: list[str], rows: list[list[str]], styles: dict[str, ParagraphStyle], widths: list[float] | None = None, small: bool = False) -> LongTable:
    t = PDFTheme()
    cell_style = styles["BodyTiny" if small else "BodySmall"]
    data = [[Paragraph(f"<b>{h}</b>", styles["BodySmall"]) for h in headers]]
    data += [[Paragraph(str(c), cell_style) for c in row] for row in rows]
    if widths:
        total = sum(widths)
        col_widths = [w / total * (A4[0] - 34 * mm) for w in widths]
    else:
        col_widths = None
    tbl = LongTable(data, colWidths=col_widths, repeatRows=1, hAlign="LEFT", splitByRow=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), t.navy),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, t.line),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FA")]),
    ]))
    return tbl


def pdf_block(block: dict[str, Any], styles: dict[str, ParagraphStyle]) -> list[Any]:
    t = PDFTheme()
    kind = block["kind"]
    if kind == "p":
        return [Paragraph(block["text"], styles["Body"])]
    if kind in {"bullets", "numbered"}:
        out = []
        for i, item in enumerate(block["items"], start=1):
            if kind == "bullets":
                out.append(Paragraph(f"• {item}", styles["Bullet"]))
            else:
                out.append(Paragraph(f"{i}. {item}", styles["Number"]))
        return out
    if kind == "flow":
        text = " <font color='#28718D'>→</font> ".join(f"<b>{x}</b>" for x in block["items"])
        tbl = Table([[Paragraph(text, styles["BodySmall"])]], colWidths=[A4[0] - 34 * mm])
        tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EDF4F6")), ("BOX", (0, 0), (-1, -1), .5, colors.HexColor("#C9DDE4")), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        return [Spacer(1, 3), tbl, Spacer(1, 5)]
    if kind == "note":
        tone = block.get("tone", "info")
        bg = colors.HexColor("#F0F6F8") if tone == "info" else colors.HexColor("#FFF8EC") if tone == "warn" else colors.HexColor("#FFF3F1")
        border = t.blue if tone == "info" else colors.HexColor("#B77A31") if tone == "warn" else t.red
        tbl = Table([[Paragraph(f'<b>{block["title"]}</b><br/>{block["text"]}', styles["BodySmall"])]], colWidths=[A4[0] - 34 * mm])
        tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg), ("LINEBEFORE", (0, 0), (0, -1), 3, border), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        return [Spacer(1, 3), tbl, Spacer(1, 5)]
    if kind == "table":
        return [Spacer(1, 3), styled_table(block["headers"], block["rows"], styles, block.get("widths"), block.get("small", False)), Spacer(1, 5)]
    raise ValueError(kind)


def build_pdf(packets: list[dict[str, Any]]) -> None:
    PDF_OUT.parent.mkdir(parents=True, exist_ok=True)
    packet_count = len(packets)
    styles = pdf_styles()
    stage_out = ROOT / "tmp" / "pdfs" / "medical_information_exam_packets_1-46.stage.pdf"
    stage_out.parent.mkdir(parents=True, exist_ok=True)
    doc = GuideDocTemplate(str(stage_out), styles)
    story: list[Any] = []
    t = PDFTheme()

    cover_box = Table([[[Paragraph("2026 EXAM / RAPID REVIEW", styles["CoverKicker"]), Paragraph(TITLE, styles["CoverTitle"]), Paragraph(SUBTITLE, styles["CoverSub"]), Paragraph(f"学習パケット1-46　｜　{packet_count}パケット　｜　確認基準日 {AS_OF}<br/>境界・業務フロー・規格の用途を、5択で判定できる粒度に整理", ParagraphStyle("CoverText", parent=styles["Body"], fontName="HeiseiKakuGo-W5", fontSize=11, leading=18, textColor=colors.white))]]], colWidths=[A4[0] - 34 * mm])
    cover_box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), t.navy), ("BOX", (0, 0), (-1, -1), 0, t.navy), ("LEFTPADDING", (0, 0), (-1, -1), 18), ("RIGHTPADDING", (0, 0), (-1, -1), 18), ("TOPPADDING", (0, 0), (-1, -1), 35), ("BOTTOMPADDING", (0, 0), (-1, -1), 35)]))
    story += [Spacer(1, 42 * mm), cover_box, Spacer(1, 23 * mm), Paragraph("第8版3冊と過去問誤答傾向に基づく個人学習用教材", ParagraphStyle("CoverFoot", parent=styles["Body"], fontName="HeiseiKakuGo-W5", alignment=TA_CENTER, textColor=t.navy)), PageBreak()]

    story += [Paragraph("使い方と収録範囲", styles["FrontTitle"]), HRFlowable(width="100%", thickness=2, color=t.blue, spaceAfter=10), Paragraph("更新版リストの学習パケット1から46を、判定目標 → 概念と比較 → 現場フロー → 引っかけ → 直前暗記の順で収録した。パケット1～3は、既習事項の再確認と5択演習に使えるよう、制度の主体・給付・請求・認定フローまで整理している。", styles["Body"])]
    scope_tbl = Table([[Paragraph("<b>S+ 1-18</b><br/>最優先・18パケット", styles["Body"]), Paragraph("<b>S 19-36</b><br/>重点・18パケット", styles["Body"]), Paragraph("<b>A 37-46</b><br/>補強・10パケット", styles["Body"])]], colWidths=[doc.width / 3] * 3)
    scope_tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), t.cyan), ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#C7E1E7")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    story += [scope_tbl, Spacer(1, 12), Paragraph("制度情報の扱い", styles["SubTitle"]), Paragraph(f"制度・法令・ガイドラインは{AS_OF}時点の一次資料を確認した。令和8年度診療報酬改定、安全管理ガイドライン第7.0版、オンライン診療指針の2026年4月一部改訂を基準とする。診療報酬の細かな点数や施設基準は出題判定に必要な範囲だけを扱う。", styles["Body"]), *pdf_block({"kind": "note", "tone": "warn", "title": "試験年度とのずれ", "text": "第8版教材や作問時点が現行制度より前の場合、版番号そのものより、本人同意・最小権限・標準規格の用途など改定後も維持される原則を優先する。"}, styles), PageBreak()]

    story += [Paragraph("目次", styles["FrontTitle"]), HRFlowable(width="100%", thickness=2, color=t.blue, spaceAfter=10)]
    toc = TableOfContents()
    toc.levelStyles = [styles["TOC0"], styles["TOC1"]]
    toc.dotsMinLevel = 0
    story += [toc, PageBreak()]

    current_group = None
    part_no = 0
    for packet in packets:
        if packet["group"] != current_group:
            current_group = packet["group"]
            part_no += 1
            story += [Spacer(1, 58 * mm), Paragraph(f"PRIORITY GROUP {part_no}", styles["PartNo"])]
            part_para = Paragraph(current_group, styles["PartTitle"])
            part_para._bookmark_key = f"part-{part_no}"
            story += [part_para, PageBreak()]

        ptitle = Paragraph(f'{packet["n"]}. {packet["title"]}', styles["PacketTitle"])
        ptitle._bookmark_key = f"packet-{packet['n']}"
        story += [Paragraph(f"PACKET {packet['n']}", styles["PacketMeta"]), ptitle, Paragraph(f'{packet["field"]}　｜　目安 {packet["minutes"]}　｜　{packet["group"]}', styles["PacketMeta"])]

        goal_content = [Paragraph(f"• {g}", styles["Bullet"]) for g in packet["goals"]]
        goal_tbl = Table([[Paragraph("<b>判定目標</b>", styles["BoxTitle"]), goal_content]], colWidths=[27 * mm, doc.width - 27 * mm])
        goal_tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), t.cyan), ("BOX", (0, 0), (-1, -1), .5, colors.HexColor("#C7E1E7")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
        story += [goal_tbl, Spacer(1, 5)]

        for section in packet["sections"]:
            story.append(Paragraph(section["title"], styles["SubTitle"]))
            for block in section["blocks"]:
                story.extend(pdf_block(block, styles))

        story.append(Paragraph("5択で狙われる引っかけ", styles["SubTitle"]))
        trap_rows = [[tr["claim"], f'<font color="#{"247153" if tr["judge"] == "○" else "A63F3F"}"><b>{tr["judge"]}</b></font>', tr["why"]] for tr in packet["traps"]]
        story += [styled_table(["選択肢として出た文", "判定", "理由"], trap_rows, styles, [38, 8, 54], small=True), Spacer(1, 8)]

        memory_items = [Paragraph(f"{i}. <b>{m}</b>", styles["Number"]) for i, m in enumerate(packet["memory"], start=1)]
        memory_tbl = Table([[Paragraph("<b>試験直前に覚えるセット</b>", styles["BoxTitle"]), memory_items]], colWidths=[45 * mm, doc.width - 45 * mm])
        memory_tbl.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), t.warm), ("LINEABOVE", (0, 0), (-1, 0), 2, colors.HexColor("#B59561")), ("BOX", (0, 0), (-1, -1), .4, colors.HexColor("#DFD3BF")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
        story += [memory_tbl]

        story.append(PageBreak())

    refs_title = Paragraph("一次資料一覧", styles["PartTitle"])
    refs_title._bookmark_key = "references"
    story += [Paragraph("APPENDIX", styles["PartNo"]), refs_title, Spacer(1, 12)]
    for sid, (name, url) in SOURCES.items():
        story.append(Paragraph(f'[{sid}] <link href="{url}" color="#146C94">{escape(name)}</link><br/><font color="#6B7880">{escape(url)}</font>', styles["Source"]))
        story.append(Spacer(1, 2))
    story += [Spacer(1, 8), Paragraph(f"URLおよび現行版は{AS_OF}に確認。本文は試験対策用の要約であり、原資料の全文を代替しない。", styles["BodySmall"])]
    doc.multiBuild(story)
    pdf_bytes = stage_out.read_bytes()
    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("Generated PDF is empty or invalid")
    PDF_OUT.write_bytes(pdf_bytes)
    stage_out.unlink()


def main() -> None:
    packets = apply_exam_updates(PACKETS_FOUNDATION + PACKETS_SPLUS + PACKETS_S + PACKETS_A)
    numbers = [p["n"] for p in packets]
    if numbers != list(range(1, 47)):
        raise ValueError(f"Packet numbers are incomplete: {numbers}")
    build_html(packets)
    build_pdf(packets)
    print(HTML_OUT)
    print(PDF_OUT)


if __name__ == "__main__":
    main()
