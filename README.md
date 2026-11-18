# hindsight_filtered

[Hindsight](https://github.com/vectorize-io/hindsight/tree/main/hindsight-integrations/hermes) の Hermes 記憶プロバイダを包み、**プラグインが会話に差し込んだターンを、ユーザーの発言として記憶させない**ための記憶プロバイダです。

[hermes-openviking-filtered](https://github.com/wararyo/hermes-openviking-filtered) の Hindsight 版です。

## なぜ必要か

[heartbeat2](https://github.com/electricsheephq/heartbeat2) などのプラグインが `ctx.inject_message` で起こしたターンは、Hermes から記憶プロバイダへ「ユーザー本人の発言」として渡されます（[NousResearch/hermes-agent#130622](https://github.com/NousResearch/hermes-agent/issues/130622)）。そのため Hindsight が、wake の指示文（`⟦pulse o:… ⟧ [HeartBeat 2.0 · wake …] Your note: …`）を `User: …` として保存し、そこから「ユーザーについての事実」を抽出してしまいます。

Hindsight の `sync_turn` は発言者の情報（`turn_author`）を受け取らないので、#130622 の修正が Hermes に入った後も、Hindsight 側が対応するまではこのプラグインが必要です。

## 何をするか

Hindsight の `sync_turn` に渡る前に、差し込まれたターンの**ユーザー側だけ**を短いラベルに差し替えます。Hindsight には次のように保存されます。

```
User: [自動ターン: HeartBeat 2.0 の予約によりエージェント自身が起動した。この行はユーザーの発言ではない]
```

- アシスタントの返事はそのまま記憶されます。wake 中にメールを確認して分かったことなどは残ります。
- 対象になるターン：
  - heartbeat2 の目印 `⟦pulse o:<id> a:<n>⟧`（グループでは ` n:<16桁hex>` 付き）を含むターン
  - `turn_author` が `{"id": "plugin:<id>", "is_bot": true}` のターン。#130622 の修正が Hermes に入った後に効きます
- それ以外（人間の発言、他の Bot の発言 `bot:<profile>`）は一切変更しません。
- 記憶の呼び出し（recall / reflect）やツール、組み込みメモリの書き込みなど、`sync_turn` 以外の動作は Hindsight そのままです。

## 前提

- Hermes Agent と、カタログ版の Hindsight プラグイン（`hermes plugins install hindsight`）がインストール済みで、`hermes memory setup` で設定済みであること
- `plugins.isolation` が既定の `in_process` であること（`host` では未検証）

## インストール（gateway を動かしているマシンで）

ディレクトリ名は `hindsight_filtered` にする必要があります。

```bash
# GitHub からインストールする場合
hermes plugins install wararyo/hermes-hindsight-filtered

# または直接 clone する場合
git clone https://github.com/wararyo/hermes-hindsight-filtered "${HERMES_HOME:-$HOME/.hermes}/plugins/hindsight_filtered"
```

記憶プロバイダを切り替えて、gateway を再起動します。

```bash
hermes config set memory.provider hindsight_filtered
hermes gateway restart
```

Hindsight の設定（`$HERMES_HOME/hindsight/config.json`、`HINDSIGHT_*` 環境変数、`~/.hindsight/`）はそのまま使われます。

## 元に戻す

```bash
hermes config set memory.provider hindsight
hermes gateway restart
```

## 注意点

- **`hermes memory setup` で Hindsight を設定し直すと、`memory.provider` が `hindsight` に戻ります。** Hindsight のセットアップが `memory.provider` を直接書き換えるためです。設定し直した後は、もう一度 `hermes config set memory.provider hindsight_filtered` を実行してください。
- プロバイダの `name` は `hindsight` のままです。ログや `hermes memory status` には `hindsight` と表示されます。
- 複数のターンをまとめて保存する設定にしていても、差し替えは各ターンが `sync_turn` に渡る時点で行われるので、まとめて保存される内容にも反映されます。
- heartbeat2 の目印の形式は、heartbeat2 0.3.14 時点のものです。形式が変わったら、`filtering.py` の `HEARTBEAT2_MARKER` を更新してください。
- 確認した Hindsight プラグインのバージョンは 1.2.4 です。Hindsight が将来 `sync_turn` で `messages` や `turn_author` を受け取るようになった場合は、このプラグインもそれらを差し替えたうえで渡します。

## 動作確認

heartbeat2 の wake が届いた後、Hindsight に保存された会話のドキュメントを確認してください。wake のターンのユーザー側が `User: [自動ターン: …]` になっていれば、正しく動いています。

## 不要になる条件

次の両方が入ったら、このプラグインは不要です。`memory.provider` を `hindsight` に戻してください。

1. Hermes：差し込まれたターンに `is_bot` の `turn_author` が付く（#130622）
2. Hindsight：`sync_turn` で `turn_author` を受け取り、`is_bot` のターンを記憶しない、または区別して扱う

## テスト

Hermes がなくても動きます。

```bash
uvx pytest tests      # または: python -m pytest tests
```
