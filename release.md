# PyPI公開手順

## 1. **パッケージのビルド**

```bash
# distディレクトリをクリーンアップ
rm -rf dist/

# ビルドツールをインストール
uv pip install build twine

# パッケージをビルド
uv run python -m build
```

## 2. **ビルド結果の確認**

```bash
# distディレクトリの内容を確認
ls dist/
# 以下のファイルが生成されているはずです：
# mcp_screen_operation-0.1.0-py3-none-any.whl
# mcp-screen-operation-0.1.0.tar.gz

# パッケージの内容を確認
tar -tf dist/mcp-screen-operation-0.1.0.tar.gz | head -20
```

## 3. **PyPIへのアップロード**

```bash
# PyPIにアップロード
twine upload dist/*

# アップロード完了後の確認
pip install mcp-screen-operation[windows]  # プラットフォームに応じて変更
```

### 4. **公開後の確認**

1. PyPIのプロジェクトページを確認：
   - https://pypi.org/project/mcp-screen-operation/

2. uvxでの動作確認：
   ```bash
   uvx mcp-screen-operation --version
   ```

### 5. **バージョンアップ時**

1. `pyproject.toml`のバージョンを更新（例: 0.1.0 → 0.1.1）
2. `CHANGELOG.md`を更新
3. gitでコミット＆タグ作成：
   ```bash
   git add -A
   git commit -m "Bump version to 0.1.1"
   git tag v0.1.1
   git push origin main --tags
   ```
4. 再度ビルド＆アップロード：
   ```bash
   rm -rf dist/
   uv run python -m build
   twine upload dist/*
   ```
