# Developer Guide

| 項目 | 内容 |
| --- | --- |
| 文書ID | `PROJECT-TEMPLATE-DEVELOPER-GUIDE` |
| 作成日 | `2026-05-02` |
| 作成者 | `tinoue` |
| 最終更新日 | `2026-05-02` |
| 最終更新者 | `tinoue (with GitHub Copilot)` |
| 版数 | `v1.0` |
| 状態 | `運用中` |

## 1. 概要

project_template の開発では、読み手が責務と境界を短時間で判断できることを重視する。
実装の振る舞いがコードだけで読み取りにくい箇所に限定して、docstring と comment を記述する。

## 2. 前提条件

- 本書は開発時の補助ガイドである
- 機械検証は module docstring の存在を最小要件として扱う

## 3. Docstring / Comment Rule

- public class / public function
  - `役割` を先に書く
  - 必要なら `返り値` `副作用` `前提` を補う
- private helper
  - すべてに機械的には書かない
  - 外部 I/O、例外吸収、状態変換、payload 整形、並行処理境界の helper を優先する
- getter / setter 相当
  - 名前の焼き直しになる docstring は書かない
- comment
  - 行単位ではなく、ブロックの意図を補うときだけ使う

悪い例:

- `start を実行する`
- `Server を表す`
- `値を取得する`

良い例:

- `バックグラウンド thread 上で server を起動し、起動完了まで待機する`
- `run 状態と metadata から公開用の平坦な payload を生成する`
- `1 回分の状態同期を保護付きで実行し、一時的な取得失敗で server を止めない`

## 4. CI での最小検証

GitHub Actions の `module-docstrings` ジョブで、次を実施する。

- 対象: `__init__.py` を除く `.py` ファイル
- 条件: モジュール先頭 docstring が存在すること
- CI 実行: `python .github/scripts/check_module_docstrings.py --root .`
- ローカル補完: `python .github/scripts/check_module_docstrings.py --root . --fix`
- 補足: 不足時は `check_module_docstrings.py --fix` で使う構成（概要 + 責務 + 責務外）に合わせたテンプレートを自動挿入する

この検証は主に存在有無を扱い、本文品質や記法（Google/Numpy/Sphinx）の厳密審査は対象外とする。
