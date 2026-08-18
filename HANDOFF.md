# 医療情報技師試験 学習HTML — GitHub Pages公開作業 引継ぎ書

作成日: 2026-08-18

## 1. 目的

46個の学習パケットを収録したインタラクティブHTMLをGitHub Pagesで配信し、iPhone/iPadのSafariやChromeで次の機能を利用できる状態にする。

- 各セクションの「ここは読んだ」チェック
- 学習進捗のブラウザ保存
- ○×問題への回答後に、正解と解説を表示
- 目次・前後リンクによるページ内移動
- 進捗データのJSON／進捗埋込みHTMLによる書き出し・読込み
- PDF版の閲覧

GitHub PagesではHTML、CSS、JavaScriptから成る静的サイトを配信できる。今回のHTMLはCSSとJavaScriptを内包しており、サーバー側処理を必要としない。

## 2. 引継ぎ成果物

ZIPを展開すると、次の構成になる。

```text
medical_information_exam_github_pages/
├── HANDOFF.md
├── build_guide.py
├── content_a.py
├── content_foundation.py
├── content_helpers.py
├── content_medical.py
├── content_reuse.py
├── content_s.py
├── content_splus.py
├── docs/
│   ├── .nojekyll
│   ├── index.html
│   └── medical_information_exam_packets_1-46.pdf
└── tmp/
    └── pdfs/
        └── DroidSansFallback.ttf
```

`docs/index.html` は、直前に生成・検証した最新HTML
`medical_information_exam_packets_1-46.html` の内容を変更せずコピーしたもの。

## 3. 現在の実装状態

- 学習パケット: 1〜46、計46パケット
- 「ここは読んだ」チェック: 288個
- インタラクティブ○×問題: 232問
- PDF: 103ページ
- HTML: CSS／JavaScriptをファイル内に内包
- PDF: 目次リンクとブックマークを実装し、印刷版では問題の正解・解説を表示
- 進捗: `localStorage` に保存し、再読込後も同じブラウザ・同じオリジンで復元

## 4. 推奨する公開方式

GitHubリポジトリの `main` ブランチに上記構成を配置し、GitHub Pagesの公開元を `main` / `/docs` に指定する。

公開ディレクトリ直下には `index.html` が必要。今回のZIPは `docs/index.html` として配置済みで、そのまま公開元にできる。

GitHub上の設定:

1. リポジトリを作成する。推奨名: `medical-information-exam-study-guide`
2. ZIP展開後の全ファイルをリポジトリ直下へ配置する。
3. `Settings` → `Pages` → `Build and deployment` を開く。
4. `Source` に `Deploy from a branch` を指定する。
5. Branchを `main`、Folderを `/docs` に指定して保存する。
6. 表示された公開URLをiOS Safariで開いて受入確認を行う。

GitHub公式資料:

- [GitHub Pagesとは](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- [ブランチからの公開設定](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [トップレベルのindex.html要件](https://docs.github.com/en/pages/getting-started-with-github-pages/troubleshooting-404-errors-for-github-pages-sites)

## 5. 変更してはいけない互換性項目

既存の学習進捗との互換性を保つため、次の値は移行処理なしに変更しない。

```javascript
const STORAGE_KEY = 'medical-information-exam-packets-4-46-progress-v1';
const DOC_ID = 'medical-information-exam-packets-4-46';
```

名称に `4-46` が残っているのは、パケット1〜3追加前の進捗との互換性を保つための仕様。ファイル名に合わせて `1-46` へ置換すると、保存済み進捗を参照できなくなる。

同様に、次の識別子も原則として維持する。

- 各チェックボックスの `data-progress-id`
- 各学習パケットとセクションのHTML ID
- JSONの `docId`

識別子を変更する場合は、旧キー・旧IDから新キー・新IDへ読み替える移行処理を実装する。

## 6. localStorageの挙動

- GitHub Pages上の進捗は、同じ端末・同じブラウザ・同じWebオリジンで保持される。
- SafariとChromeは保存領域を共有しない。iPhoneとMacなど端末間でも自動同期しない。
- `file://` で開いたローカルHTMLの保存領域から、GitHub Pagesの `https://` オリジンへ進捗は自動移行しない。
- 既存進捗がある場合は、ローカル版でJSONを書き出し、公開版で読み込む。
- GitHub Pagesのユーザー名ドメインから独自ドメインへ移行するとオリジンが変わるため、JSON移行が必要。
- Safariの履歴・Webサイトデータ消去やプライベートブラウズでは、進捗が失われる可能性がある。

## 7. ソース更新と再生成

教材本文は次のPythonファイルで管理している。

- `content_foundation.py`: パケット1〜3
- `content_splus.py`: S+領域
- `content_s.py`: S領域
- `content_a.py`: A領域
- `content_medical.py`, `content_reuse.py`, `content_helpers.py`: 共通・補助データ
- `build_guide.py`: HTML／PDF生成

現行の `build_guide.py` は次の出力先を使う。

```python
HTML_OUT = ROOT / "output" / "html" / "medical_information_exam_packets_1-46.html"
PDF_OUT = ROOT / "output" / "pdf" / "medical_information_exam_packets_1-46.pdf"
```

GitHub Pages運用では、生成後に成果物を `docs` へコピーするか、出力先を次のように変更する。

```python
HTML_OUT = ROOT / "docs" / "index.html"
PDF_OUT = ROOT / "docs" / "medical_information_exam_packets_1-46.pdf"
```

PDF生成にはPythonとReportLabを使用する。日本語フォントは `tmp/pdfs/DroidSansFallback.ttf` に同梱している。生成後はHTMLとPDFの双方を確認してからコミットする。

## 8. 公開前の受入確認

iOS Safariで次の項目を確認する。

1. トップページと目次が表示される。
2. パケット1のQ1「市町村国保の保険者は市町村だけである。」で「×」を選ぶと、正解表示と解説が現れる。
3. パケット1の「判定目標」で「ここは読んだ」を選ぶと、全体進捗が更新される。
4. ページを再読込してもチェック状態が残る。
5. 「回答をやり直す」で選択状態が初期化される。
6. 目次、前のパケット、次のパケット、ページ上部へ戻るリンクが機能する。
7. 進捗JSONの書き出しと読込みが機能する。
8. `medical_information_exam_packets_1-46.pdf` を公開URLから開ける。
9. SafariのWebインスペクタまたはデスクトップChromeのDevToolsでJavaScriptエラーが発生していない。

## 9. 公開範囲と注意事項

GitHub Pagesは原則として公開Webサイトとして扱う。リポジトリを非公開にしても、プランや設定によってPagesサイト自体が公開される場合がある。アクセス制限が必要なら、GitHub Pagesを公開先として採用する前に要件を再確認する。

公開前に次を確認する。

- 個人情報や試験回答履歴をHTMLへ埋め込んでいない。
- 市販教材の紙面画像や長い転載文を含めていない。
- 検索結果への掲載を望まない場合でも、`noindex` はアクセス制限にはならない。

## 10. 次のCodexへ渡す依頼文

```text
添付ZIPとHANDOFF.mdを前提に、医療情報技師試験の学習HTMLをGitHub Pagesで公開できるリポジトリ構成にしてください。

公開元は main ブランチの /docs を使用します。docs/index.html は最新HTMLなので、学習内容と既存の進捗IDを変更しないでください。特に STORAGE_KEY、DOC_ID、data-progress-id は互換性維持のため変更しないでください。

必要な作業は、リポジトリへの配置、GitHub Pages設定、公開URLでの動作確認です。iOS Safariで、○×回答後の正解・解説表示、「ここは読んだ」の保存・再読込、目次リンク、進捗JSONの書き出し・読込み、PDF表示を確認してください。

ソースを更新する場合は build_guide.py と content_*.py を正本とし、生成後のHTMLを docs/index.html、PDFを docs/medical_information_exam_packets_1-46.pdf に反映してください。
```

## 11. 引継ぎ判断

- **公開だけを行う場合**: `docs/index.html` と `docs/medical_information_exam_packets_1-46.pdf` があれば足りる。
- **学習内容を今後も修正・再生成する場合**: HTML単体ではなく、生成スクリプト、`content_*.py`、フォントを含むZIP全体を渡す。
- **最新HTMLの扱い**: 先ほど生成したHTMLをそのまま渡してよい。GitHub Pagesではファイル名を `index.html` として公開ディレクトリ直下へ配置する。
