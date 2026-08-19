from __future__ import annotations

from typing import Any

from content_helpers import FLOW, NOTE, P, SEC, TABLE, TRAP, UL


def _packet(packets: list[dict[str, Any]], title: str) -> dict[str, Any]:
    for packet in packets:
        if packet["title"] == title:
            return packet
    raise KeyError(title)


def _section(packet: dict[str, Any], title_prefix: str) -> dict[str, Any]:
    for section in packet["sections"]:
        if section["title"].startswith(title_prefix):
            return section
    raise KeyError(f'{packet["title"]}: {title_prefix}')


def _extend_once(packet: dict[str, Any]) -> bool:
    if packet.get("_exam_updates_applied"):
        return False
    packet["_exam_updates_applied"] = True
    return True


def apply_exam_updates(packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Add compact 2021-2025 past-question coverage updates without renumbering existing sections."""
    _update_foundation(_packet(packets, "診療報酬・DPC/PDPS・歯科"))
    _update_his(_packet(packets, "HIS全体像・電子カルテ・オーダ"))
    _update_nursing(_packet(packets, "看護情報システム"))
    _update_drugs(_packet(packets, "医薬品・薬機法・処方箋"))
    _update_ihe(_packet(packets, "IHE / SS-MIX2"))
    _update_safety_gl(_packet(packets, "医療情報システム安全管理GL"))
    _update_public_health(_packet(packets, "公衆衛生・予防・地域医療"))
    _update_regional(_packet(packets, "介護・健診・地域連携システム"))
    _update_research(_packet(packets, "CRF・EDC・ODM"))
    _update_network(_packet(packets, "ネットワーク基礎・仮想化"))
    _update_firewall(_packet(packets, "NAT・DMZ・Firewall"))
    _update_tests(_packet(packets, "検体検査・検査精度"))
    _update_images(_packet(packets, "画像・核医学"))
    _update_ris(_packet(packets, "RIS・PACS・画像連携"))
    _update_departments(_packet(packets, "中央診療部門"))
    _update_devices(_packet(packets, "医療安全部門"))
    _update_storage(_packet(packets, "RAID・ストレージ"))
    _update_wifi(_packet(packets, "LAN・Wi-Fi"))
    _update_availability(_packet(packets, "可用性・障害対策"))
    _update_auth(_packet(packets, "LDAP・認証"))
    _update_it_basics(_packet(packets, "UML"))
    _update_medical_basics(_packet(packets, "生理機能検査"))
    return packets


def _update_foundation(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    packet["sections"].append(
        SEC(
            "5. 歯科・口腔で狙われる疾患名",
            TABLE(
                ["用語", "見分ける軸", "試験での境界"],
                [
                    ["う蝕", "歯の硬組織が脱灰・崩壊", "いわゆるむし歯。歯髄炎や根尖性歯周炎へ進むことがある。"],
                    ["歯周病", "歯肉・歯周組織の炎症と破壊", "う蝕とは病変部位が異なる。歯周ポケット、歯槽骨吸収等。"],
                    ["歯髄炎／根尖性歯周炎", "歯髄・根尖周囲の炎症", "保存処置、根管治療などと結び付けて読む。"],
                    ["口内炎／口唇ヘルペス", "粘膜炎症／ウイルス性水疱", "歯科疾患名と感染症名を混同しない。"],
                    ["補綴・保存・口腔外科", "欠損補う／歯を保存／抜歯等", "歯科レセプトでは処置・材料・補綴物を区別する。"],
                ],
                [22, 38, 40],
                small=True,
            ),
        )
    )
    packet["memory"].append("歯科は、う蝕＝歯、歯周病＝歯周組織、補綴＝欠損補う、保存＝歯を残す処置。")


def _update_his(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    _section(packet, "1. HIS")["blocks"].extend(
        [
            TABLE(
                ["階層", "意味", "例"],
                [
                    ["データ", "観察・測定された個々の値", "体温、検査値、処方コード、画像属性。"],
                    ["情報", "目的に沿って整理されたデータ", "患者サマリー、検査結果一覧、入退院履歴。"],
                    ["知識", "判断に使える規則・解釈", "禁忌、診療ガイドライン、アラートルール。"],
                    ["知恵", "状況・価値観を踏まえた意思決定", "患者背景を考慮した治療選択。"],
                ],
                [18, 36, 46],
            ),
            TABLE(
                ["導入語", "何をするか", "境界"],
                [
                    ["RFI", "情報提供依頼", "市場・製品・概算を調べる。契約条件そのものではない。"],
                    ["RFP", "提案依頼", "要求仕様・評価条件を示し、ベンダ提案を比較する。"],
                    ["要求仕様書", "必要機能・非機能を文書化", "現場要望をそのまま並べず、業務目的と優先度を明確にする。"],
                    ["受入試験", "納入物が要求を満たすか確認", "単体・結合試験だけでは、利用部門の受入判断にならない。"],
                ],
                [20, 34, 46],
            ),
        ]
    )
    packet["memory"].append("導入はRFIで情報収集、RFPで提案依頼、要求仕様で判定条件、受入試験で採否確認。")


def _update_nursing(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    _section(packet, "3. 看護独自情報")["blocks"].append(
        TABLE(
            ["看護管理情報", "用途", "注意"],
            [
                ["勤務表・配置", "必要人員、資格、夜勤、病棟負荷の調整", "労務管理だけでなく安全な看護提供体制に関わる。"],
                ["重症度、医療・看護必要度", "患者状態と看護・処置の必要性を評価", "DPC調査Hファイル等とも関連する。"],
                ["病棟日誌", "病棟単位の出来事、入退院、勤務状況を記録", "個々の診療録・看護記録とは目的が異なる。"],
            ],
            [24, 40, 36],
        )
    )
    packet["memory"].append("看護管理＝勤務・配置・必要度・病棟日誌。個別看護記録とは粒度が違う。")


def _update_drugs(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    _section(packet, "1. 薬機法")["blocks"].append(
        TABLE(
            ["頻出項目", "押さえる点", "混同しやすい点"],
            [
                ["薬物動態", "吸収・分布・代謝・排泄。代謝は肝臓、排泄は腎臓・胆汁が代表。", "血中濃度だけで薬効・副作用は決まらない。"],
                ["剤形", "錠剤、カプセル剤、散剤、顆粒剤、注射剤、外用剤など。", "剤形と毒性区分・処方箋医薬品区分は別軸。"],
                ["後発医薬品", "先発医薬品と有効成分・効能効果等が同等と承認された医薬品。", "バイオシミラーはバイオ医薬品の後続品として区別して出る。"],
                ["特定生物由来製品", "感染症リスク等に備え、使用記録を長期保存する。", "通常の添付文書確認だけで終わらない。"],
                ["添付文書電子化", "原則電子的提供。紙同梱の例外やGS1コードからの閲覧を問われる。", "最新版確認と紙添付の有無を分ける。"],
            ],
            [20, 44, 36],
            small=True,
        )
    )
    _section(packet, "2. 規制区分")["blocks"].append(
        TABLE(
            ["麻薬管理", "要点", "代表的な選択肢境界"],
            [
                ["免許", "麻薬施用者免許等は都道府県知事が交付する。", "施設の一般許可や医師免許とは別。"],
                ["処方箋", "患者情報、麻薬名、分量、用法、施用者情報等を確認する。", "通常処方箋より記載・管理が厳格。"],
                ["事故届", "滅失・盗取・所在不明等は届出対象。", "帳簿訂正だけで済ませない。"],
            ],
            [20, 44, 36],
        )
    )
    _section(packet, "3. 処方箋")["blocks"].extend(
        [
            TABLE(
                ["電子処方箋語", "意味", "試験での境界"],
                [
                    ["HPKI", "医師・歯科医師・薬剤師等の資格を確認できる公開鍵基盤", "電子署名の本人性・資格確認に使う。"],
                    ["ローカル署名／リモート署名", "署名処理を端末側／遠隔署名サービス側で行う方式", "どちらも署名者確認と鍵管理が重要。"],
                    ["引換番号", "処方箋ごとに発行される番号", "患者IDではない。資格確認書等で薬局が処方箋を取り出す際に使う。"],
                    ["調剤結果登録", "薬局が調剤後の情報を管理サービスへ登録", "処方登録だけで薬剤情報共有が完結するわけではない。"],
                ],
                [24, 43, 33],
                small=True,
            ),
            NOTE("電子版お薬手帳", "薬剤情報、服薬情報、アレルギー・副作用歴等を本人中心に管理し、マイナポータル連携や薬剤師との共有に使う。電子処方箋管理サービスそのものとは役割が異なる。", "info"),
        ]
    )
    packet["memory"].extend(
        [
            "薬物動態＝吸収・分布・代謝・排泄。肝代謝、腎排泄が代表。",
            "HPKI＝医療資格者の電子署名基盤。引換番号＝処方箋ごとの受付補助番号。",
        ]
    )


def _update_ihe(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    _section(packet, "1. IHE")["blocks"].append(
        TABLE(
            ["プロファイル", "主な用途", "一言"],
            [
                ["XCA", "コミュニティ間の文書照会・取得", "地域連携ネットワークを越えた参照。"],
                ["XDS-I", "画像文書・画像参照の共有", "DICOM画像そのものの保存標準とは分ける。"],
                ["MHD", "FHIR等を用いた文書共有アクセス", "モバイル・Web API寄りの文書アクセス。"],
                ["CT", "時刻同期", "監査ログやイベント時刻の整合に重要。"],
            ],
            [22, 46, 32],
        )
    )
    packet["memory"].append("IHE追加頻出＝XDS文書共有、XCA地域間、XDS-I画像共有、PIX/PDQ患者同定、ATNA監査、CT時刻同期。")


def _update_safety_gl(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    _section(packet, "1. 2026")["blocks"].append(
        TABLE(
            ["版", "出題で見るポイント", "注意"],
            [
                ["第5.1版", "電子保存・外部保存・運用管理の基本", "過去問では版番号を当時基準で問うことがある。"],
                ["第5.2版", "二要素認証やサイバー対策の強化", "現行版との差分問題では時点を読む。"],
                ["第6.0版", "概説・経営管理・企画管理・運用に再構成", "2025年問題ではこの版を前提にした記述が出る。"],
                ["第7.0版", "保守委託機関編を含め、委託先の役割も明確化", "2026年6月公表の現行版。"],
            ],
            [18, 47, 35],
        )
    )
    _section(packet, "3. 委託")["blocks"].append(
        TABLE(
            ["用語", "意味", "運用上の要点"],
            [
                ["フォレンジック", "事故後に証拠保全・原因調査を行う技術・手続", "ログ、端末、通信、時刻を保全し、復旧優先と証拠保全を両立する。"],
                ["ブレークグラス", "緊急時に通常権限外でアクセスする例外運用", "理由、範囲、強いログ、事後監査を必ず伴う。"],
                ["サイバー初動", "隔離、連絡、影響範囲把握、BCP発動、復旧判断", "証拠を消す再起動・一括削除を安易に行わない。"],
            ],
            [20, 42, 38],
        )
    )
    packet["memory"].append("安全管理GLは出題年の版を読む。第6.0版は2025年問題、第7.0版は2026年6月現行。")


def _update_public_health(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    _section(packet, "1. 予防段階")["blocks"].append(
        TABLE(
            ["用語", "要点", "境界"],
            [
                ["BMI", "体重kg ÷ 身長m²", "身長はmで二乗。体脂肪率そのものではない。"],
                ["メタボリックシンドローム", "内臓脂肪蓄積を基盤に、血圧・血糖・脂質異常を組み合わせて判定", "単なる肥満やBMIだけでは判定しない。"],
                ["特定健診", "40〜74歳の医療保険加入者を保険者が実施", "学校健診・職域の一般健診・診療上の検査と区別。"],
            ],
            [22, 46, 32],
        )
    )
    _section(packet, "3. 救急医療")["blocks"].append(
        TABLE(
            ["トリアージ色", "優先度", "意味"],
            [
                ["赤", "最優先治療群", "直ちに処置が必要。"],
                ["黄", "待機的治療群", "処置は必要だが赤より待てる。"],
                ["緑", "軽処置群", "歩行可能など比較的軽症。"],
                ["黒", "死亡・救命困難群", "救命困難または死亡。紫を通常色として選ばない。"],
            ],
            [20, 30, 50],
        )
    )
    packet["memory"].append("BMI＝kg/m²、メタボ＝内臓脂肪＋血圧・血糖・脂質、トリアージ＝赤黄緑黒。")


def _update_regional(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    _section(packet, "3. 地域医療連携")["blocks"].extend(
        [
            TABLE(
                ["医療DXの狙い", "一言"],
                [
                    ["国民の更なる健康増進", "本人が情報を活用し予防・受診につなげる。"],
                    ["切れ目なく質の高い医療等の効率的提供", "医療・介護間で必要情報を共有する。"],
                    ["医療機関等の業務効率化", "入力・確認・請求等の重複を減らす。"],
                    ["システム人材等の有効活用", "共通基盤・標準化で個別改修負荷を下げる。"],
                    ["医療情報の二次利用環境整備", "研究・政策・品質改善に使える基盤を整える。"],
                ],
                [34, 66],
            ),
            TABLE(
                ["共有対象", "具体例", "境界"],
                [
                    ["3文書", "診療情報提供書、退院時サマリー、健康診断結果報告書", "紹介・退院・健診の文書共有。"],
                    ["6情報", "傷病名、薬剤アレルギー等、その他アレルギー等、感染症、検査、処方", "全国の医療機関等や本人等の閲覧対象として問われる。"],
                    ["患者サマリー", "療養上の計画やアドバイス等", "本人等の閲覧を想定する要約情報。"],
                ],
                [22, 50, 28],
                small=True,
            ),
        ]
    )
    packet["memory"].append("電子カルテ情報共有サービス＝3文書＋6情報＋患者サマリー。資格確認だけの仕組みではない。")


def _update_research(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    _section(packet, "3. CDISC")["blocks"].append(
        TABLE(
            ["CDISC標準", "用途", "覚え方"],
            [
                ["CDASH", "CRFで収集する項目の標準", "集め方。"],
                ["SDTM", "規制提出向けの標準データ構造", "提出用に並べる。"],
                ["ADaM", "解析用データセット", "統計解析に使う。"],
                ["ODM", "臨床試験データ・メタデータ交換", "XMLベースの交換。"],
            ],
            [20, 48, 32],
        )
    )
    packet["memory"].append("CDISCはCDASH＝収集、SDTM＝提出、ADaM＝解析、ODM＝交換。")


def _update_network(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    _section(packet, "1. 通信")["blocks"].append(
        TABLE(
            ["プロトコル", "主な役割", "代表ポート・補足"],
            [
                ["HTTP / HTTPS", "Web通信", "80 / 443。HTTPSはTLSで保護。"],
                ["SMTP", "メール送信・転送", "25、587等。IMAP4/POP3とは用途が違う。"],
                ["IMAP4 / POP3", "メール閲覧・取得", "IMAP4はサーバ上管理、POP3は端末取得が中心。"],
                ["SSH", "暗号化された遠隔ログイン等", "22。Telnetより安全。"],
                ["NTP", "時刻同期", "123。ログ整合や認証に重要。"],
                ["ARP / ICMP", "IPv4のIP→MAC解決／疎通・エラー通知", "pingはICMPを使う。IPv6では近隣探索を用いる。"],
            ],
            [22, 42, 36],
            small=True,
        )
    )
    _section(packet, "2. DNS")["blocks"].append(
        NOTE("IPv6", "IPv4は32bit、IPv6は128bit。IPv6ではブロードキャストではなくマルチキャスト等を用い、ARPではなく近隣探索で同一リンク内の解決を行う。", "info")
    )
    packet["memory"].append("代表ポート＝HTTP80、HTTPS443、SSH22、NTP123。SMTP送信、IMAP4閲覧、ARP/ICMPは役割別。")


def _update_firewall(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    _section(packet, "1. 境界機能")["blocks"].append(
        TABLE(
            ["攻撃・対策", "意味", "境界"],
            [
                ["SQLインジェクション", "入力値を悪用してSQLを不正実行", "WAFだけでなく、プレースホルダ、入力検証、権限分離を使う。"],
                ["Cookie窃取・改ざん", "セッション情報等の悪用", "HttpOnly、Secure、SameSite、TLS等で保護する。"],
                ["フィッシング", "偽サイト・偽メールで資格情報を奪う", "認証強化、教育、メール対策、URL確認。"],
                ["ゼロデイ", "修正前の未知・未公表脆弱性を悪用", "多層防御、監視、緩和策、迅速な更新。"],
            ],
            [24, 42, 34],
            small=True,
        )
    )
    packet["memory"].append("Web防御はFirewallだけでなく、WAF、入力検証、Cookie保護、脆弱性管理を組み合わせる。")


def _update_tests(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    _section(packet, "1. 検体")["blocks"].append(
        TABLE(
            ["検査名", "主な対象", "代表的に結び付く疾患・状態"],
            [
                ["CRP", "炎症反応", "感染症・炎症。原因疾患の特定は他所見と統合する。"],
                ["HbA1c／血糖", "糖代謝", "糖尿病。HbA1cは過去1〜2か月程度の血糖状態の目安。"],
                ["AST／ALT／γ-GTP／ALP", "肝胆道系", "肝障害、胆道系異常。ASTは心筋等にも存在する。"],
                ["eGFR／尿蛋白", "腎機能・腎障害", "CKD評価で頻出。血清クレアチニン等と合わせる。"],
                ["AFP／CEA／CA19-9", "腫瘍マーカー", "診断確定ではなく、補助・経過観察に使う。"],
                ["血液ガス", "pH、PaO2、PaCO2、HCO3-", "呼吸不全、酸塩基平衡。動脈血ガスABG/ABGAが代表。"],
            ],
            [23, 32, 45],
            small=True,
        )
    )
    packet["memory"].append("検査名は疾患確定ではなく手掛かり。CRP炎症、HbA1c糖尿病、eGFR腎、AFP/CEA/CA19-9腫瘍マーカー。")


def _update_images(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    _section(packet, "2. CT")["blocks"].append(
        TABLE(
            ["検査・手技", "要点", "狙われる境界"],
            [
                ["MRI", "強磁場とRFを用いる。金属・植込み機器・吸着事故に注意。", "X線被ばくはないが、安全確認は重い。"],
                ["MRA", "血管を描出するMRI手法。条件により非造影でも撮像可能。", "造影CT angiographyと混同しない。"],
                ["超音波", "反射波で観察。リアルタイム性が強み。", "腸管ガス、骨、肺の含気で観察困難なことがある。"],
                ["上部消化管内視鏡", "食道・胃・十二指腸を観察", "大腸内視鏡とは観察範囲が違う。"],
            ],
            [22, 44, 34],
        )
    )
    _section(packet, "4. マンモ")["blocks"].append(
        TABLE(
            ["治療・処置", "概要", "代表例・境界"],
            [
                ["IVR", "画像誘導下に診断・治療を行う", "血管塞栓、血管形成、生検、ドレナージ等。血管造影だけではない。"],
                ["放射線治療", "治療計画、位置決め、照射、効果・副作用評価", "画像診断や核医学検査とは目的が異なる。"],
                ["血液透析", "半透膜を介して老廃物・水分等を除去", "腎不全治療。透析条件・体重・抗凝固等を管理。"],
                ["ECMO", "体外で酸素化・二酸化炭素除去を補助", "人工呼吸器や通常透析と役割が違う。"],
                ["カテーテルアブレーション", "不整脈の原因部位を焼灼等で治療", "検査カテーテルや血管造影だけではない。"],
            ],
            [23, 43, 34],
            small=True,
        )
    )
    packet["memory"].append("MRAは血管MRI、USはガス・骨・肺が苦手、上部内視鏡は食道・胃・十二指腸。")


def _update_ris(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    _section(packet, "3. 画像ライフサイクル")["blocks"].append(
        TABLE(
            ["画像データ語", "意味", "境界"],
            [
                ["画素・解像度", "画像を構成する点とその数", "画素数が多いほど容量は増えやすい。診断能は撮影条件・表示品質も影響。"],
                ["階調・色深度", "1画素あたりの濃淡・色の段階数", "n bitなら2^n階調。医用画像では階調管理が重要。"],
                ["可逆圧縮／非可逆圧縮", "完全復元できる／一部情報を捨てる", "診療用途では画質要件と保存方針を確認する。"],
                ["JPEG／PNG／TIFF", "画像形式", "JPEGは一般に非可逆圧縮も用いる。PNGは可逆圧縮が中心。"],
            ],
            [22, 42, 36],
            small=True,
        )
    )
    packet["memory"].append("画像データは画素数・階調・圧縮で容量と品質が変わる。可逆は戻る、非可逆は情報を捨てる。")


def _update_departments(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    _section(packet, "1. 共通骨格")["blocks"].append(
        TABLE(
            ["部門", "固有情報", "狙われる語"],
            [
                ["眼科", "視力、眼圧、屈折、視野、眼底、OCT", "画像・計測値・左右眼を管理する。"],
                ["耳鼻咽喉科", "聴力、ティンパノメトリー、内視鏡、平衡機能", "聴力検査と画像検査を混同しない。"],
                ["産科", "妊娠週数、分娩経過、胎児心拍、パルトグラム", "母体と胎児の情報を時間経過で扱う。"],
                ["外来化学療法", "レジメン、体表面積、投与量、前投薬、血液検査", "薬剤量と実施可否を多職種で確認する。"],
                ["病理", "標本受付、標本番号、病理診断、免疫染色", "検体・標本・報告書の追跡性が重要。"],
                ["血液浄化", "透析条件、透析記録、装置連携、透析液管理", "通常の採血検査や輸血管理とは別部門。"],
            ],
            [20, 44, 36],
            small=True,
        )
    )
    packet["memory"].append("部門固有語＝眼科OCT、産科パルトグラム、化学療法レジメン、病理標本番号、血液浄化透析条件。")


def _update_devices(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    _section(packet, "3. 報告データ")["blocks"].append(
        TABLE(
            ["医療機器管理", "台帳・記録で見る項目", "境界"],
            [
                ["機器台帳", "製造販売業者、型式、シリアル番号、購入日、設置場所、耐用期間", "患者記録ではなく機器資産・安全管理情報。"],
                ["保守点検", "点検日、実施者、点検結果、修理履歴、次回予定", "故障時だけでなく定期点検を管理する。"],
                ["安全情報", "回収、添付文書改訂、不具合報告", "医療材料在庫や薬剤副作用報告と混同しない。"],
            ],
            [22, 48, 30],
        )
    )
    packet["memory"].append("医療機器管理＝台帳＋保守点検＋不具合・回収情報。型式・シリアル・場所を追跡する。")


def _update_storage(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    packet["sections"].append(
        SEC(
            "4. コンピュータ構成と記憶媒体",
            TABLE(
                ["分類", "代表語", "要点"],
                [
                    ["5大装置", "入力、出力、記憶、演算、制御", "CPUは演算・制御、主記憶は実行中データ、補助記憶は永続保存。"],
                    ["CPU動作", "命令フェッチ、デコード、実行", "クロック、キャッシュ、主記憶アクセスを区別。"],
                    ["記憶媒体", "HDD、SSD、フラッシュメモリ、CD/DVD/Blu-ray、LTO", "SSDは半導体、HDDは磁気ディスク、光ディスクはレーザー。"],
                    ["OS周辺", "カーネル、シェル、ドライバ、ファームウェア、BIOS/UEFI", "OS本体・利用者窓口・機器制御・機器内蔵制御を分ける。"],
                    ["接続", "USB、HDMI、DisplayPort、RJ-45", "データ、映像、ネットワーク等の用途を対応づける。"],
                ],
                [18, 36, 46],
                small=True,
            ),
        )
    )
    packet["memory"].append("CPU＝フェッチ・デコード・実行。カーネル＝OS中核、シェル＝操作窓口、ドライバ＝機器制御。")


def _update_wifi(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    _section(packet, "2. Wi-Fi")["blocks"].append(
        TABLE(
            ["無線・物理語", "意味", "境界"],
            [
                ["IEEE 802.11a/b/g/n/ac/ax", "無線LAN規格群", "周波数帯、速度、チャネル幅、互換性を区別する。"],
                ["MIMO", "複数アンテナで通信容量・品質を高める", "単にAP台数を増やすことではない。"],
                ["DFS", "気象レーダ等との干渉を避けチャネルを変更", "5GHz帯設計で問われる。"],
                ["UTP／光ファイバ", "銅線ツイストペア／光伝送", "光はシングルモード・マルチモードの距離差も出る。"],
            ],
            [24, 42, 34],
        )
    )
    packet["memory"].append("Wi-Fiは802.11規格、MIMO、DFS、チャネル、電波干渉、UTP/光ファイバをまとめて判定する。")


def _update_availability(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    _section(packet, "2. 切替")["blocks"].append(
        TABLE(
            ["構成・提供形態", "意味", "境界"],
            [
                ["ホットスタンバイ", "待機系が稼働状態で短時間切替", "コストは高いがRTOを短くしやすい。"],
                ["ウォームスタンバイ", "一部準備済みで起動・同期後に切替", "ホットとコールドの中間。"],
                ["コールドスタンバイ", "停止状態から準備して切替", "安価だが復旧時間は長い。"],
                ["SaaS / PaaS / IaaS", "アプリ／実行基盤／仮想資源をサービス利用", "オンプレミスや単なるホスティングと責任分界を読む。"],
            ],
            [24, 42, 34],
            small=True,
        )
    )
    _section(packet, "3. RTO")["blocks"].append(
        TABLE(
            ["テスト・保守", "目的", "一言"],
            [
                ["単体／結合／システム／受入テスト", "部品、連携、全体、利用者受入を順に確認", "受入テストは発注者・利用部門の確認。"],
                ["性能／負荷／回帰テスト", "応答、限界、修正後の影響を確認", "正常系だけではない。"],
                ["予防／是正／適応保守", "故障予防、障害修正、環境変化対応", "機能追加・法改正対応も保守として出る。"],
            ],
            [26, 44, 30],
        )
    )
    packet["memory"].append("ホット・ウォーム・コールドは待機度合い。テストは単体→結合→システム→受入。")


def _update_auth(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    _section(packet, "2. 認証")["blocks"].append(
        TABLE(
            ["PKI語", "意味", "判定点"],
            [
                ["CA", "認証局。証明書を発行・失効管理する", "公開鍵そのものの信頼を保証する。"],
                ["デジタル証明書", "主体と公開鍵を結び付ける電子的証明", "期限、失効、発行元、主体名を検証する。"],
                ["電子署名", "秘密鍵で署名し、公開鍵で検証", "本人性・改ざん検知。暗号化とは目的が違う。"],
                ["ハッシュ／メッセージダイジェスト", "データから固定長値を作る", "改ざん検知に使うが、単独では本人性を示さない。"],
            ],
            [22, 40, 38],
        )
    )
    packet["memory"].append("PKI＝CAが証明書で公開鍵を信頼させる。署名は秘密鍵で作り公開鍵で検証、ハッシュは改ざん検知。")


def _update_it_basics(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    packet["sections"].append(
        SEC(
            "4. 情報表現・プログラミング・開発管理",
            TABLE(
                ["領域", "頻出語", "判定の核"],
                [
                    ["数値表現", "bit、Byte、2進、16進、k/M/G/T、2の補数", "1Byte＝8bit。2進4bitが16進1桁。接頭辞と単位を読む。"],
                    ["論理演算", "AND、OR、XOR、NOT、NAND、NOR", "ANDは両方1、ORはどちらか1、XORは異なると1。"],
                    ["デジタル化", "標本化、量子化、符号化、ナイキスト周波数", "最大周波数の2倍以上で標本化。量子化bit数で階調数が決まる。"],
                    ["データ構造", "配列、リスト、スタック、キュー、木", "スタックはLIFO、キューはFIFO。"],
                    ["言語処理", "コンパイラ、インタプリタ、ソースコード、デバッグ", "一括翻訳と逐次実行を区別する。"],
                    ["開発モデル", "ウォーターフォール、アジャイル、プロトタイピング", "工程順序固定か、反復・適応かを読む。"],
                    ["管理技法", "WBS、ガントチャート、PERT、クリティカルパス", "作業分解、日程可視化、依存関係と最長経路。"],
                    ["新技術", "IoT、AR、VR、生成AI、ハルシネーション", "ARは現実重畳、VRは仮想空間、生成AIはもっともらしい誤りに注意。"],
                ],
                [20, 40, 40],
                small=True,
            ),
            NOTE("フローチャートとトレース", "開始・終了、処理、判断、入出力を記号で表し、変数の値を上から順に追う。繰返しでは初期値、終了条件、更新処理を確認する。", "info"),
        )
    )
    packet["memory"].extend(
        [
            "1Byte＝8bit、16進1桁＝2進4bit、スタック＝LIFO、キュー＝FIFO。",
            "標本化→量子化→符号化。ナイキストは最大周波数の2倍以上。",
            "WBS＝作業分解、ガント＝日程表、PERT＝依存関係、クリティカルパス＝最長経路。",
        ]
    )


def _update_medical_basics(packet: dict[str, Any]) -> None:
    if not _extend_once(packet):
        return
    packet["sections"].append(
        SEC(
            "5. 人体・疾患・検査の基本対応",
            TABLE(
                ["項目", "代表語", "試験での境界"],
                [
                    ["脳幹", "中脳、橋、延髄", "大脳・小脳と区別。生命維持機能と関連する。"],
                    ["動脈血の流れ", "肺静脈→左心房→左心室→大動脈", "肺動脈は静脈血を肺へ送る点に注意。"],
                    ["腹腔内臓器", "肝臓、胆嚢、膵臓、脾臓、小腸、大腸など", "肺・心臓は胸腔。腎臓は後腹膜臓器として問われることがある。"],
                    ["代謝・内分泌", "糖尿病、甲状腺疾患、痛風", "膵臓ホルモンはインスリンとグルカゴンが代表。"],
                    ["呼吸器", "気管支喘息、COPD、肺炎、睡眠時無呼吸症候群", "スパイロメトリー、PSG、血液ガスと結び付ける。"],
                    ["血液・造血", "貧血、白血病、血小板異常", "血算、血液像、骨髄検査が代表。"],
                    ["神経", "てんかん、脳梗塞、パーキンソン病", "EEGはてんかん性放電、CT/MRIは形態・病変評価。"],
                    ["新生児", "アプガースコア、NICU", "心拍、呼吸、筋緊張、反射、皮膚色を評価。"],
                    ["治療目的", "根治的、姑息的、対症療法、リハビリ", "治癒を目指すか、症状緩和・機能回復かで判定する。"],
                ],
                [20, 38, 42],
                small=True,
            ),
        )
    )
    packet["memory"].append("人体対応＝脳幹は中脳・橋・延髄、動脈血は肺静脈→左心→大動脈、膵ホルモンはインスリン・グルカゴン。")

