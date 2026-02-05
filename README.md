# NotePM MCP Server

NotePMのコンテンツを検索するためのModel Context Protocol (MCP) サーバーです。このサーバーを使用することで、NotePMの検索機能をMCP対応のクライアントから利用することができます。

## 機能

### ページ操作
- `notepm_search` - NotePMのコンテンツ全文検索（タイトルのみ、タグ、ノートコードによる検索も可能）
- `notepm_page_detail` - 詳細な記事の内容を取得
- `notepm_page_create` - 新しいページを作成
- `notepm_page_update` - ページの更新
- `notepm_page_delete` - ページの削除

### ノート操作
- `notepm_note_list` - ノート一覧の取得
- `notepm_note_detail` - ノートの詳細を取得
- `notepm_note_create` - 新しいノートを作成
- `notepm_note_update` - ノートの更新
- `notepm_note_delete` - ノートの削除
- `notepm_note_archive` - ノートをアーカイブ
- `notepm_note_unarchive` - ノートのアーカイブを解除

### フォルダ操作
- `notepm_folder_list` - フォルダ一覧の取得
- `notepm_folder_create` - 新しいフォルダを作成

### コメント操作
- `notepm_comment_search` - コメントの検索
- `notepm_comment_create` - コメントの作成
- `notepm_comment_update` - コメントの更新
- `notepm_comment_delete` - コメントの削除

### 添付ファイル操作
- `notepm_attachment_search` - 添付ファイルの検索
- `notepm_attachment_download` - 添付ファイルのダウンロード情報取得
- `notepm_attachment_delete` - 添付ファイルの削除
- `notepm_attachment_upload` - 添付ファイルのアップロード

### タグ操作
- `notepm_tag_search` - タグ一覧の取得
- `notepm_tag_create` - タグの作成
- `notepm_tag_delete` - タグの削除

### ユーザー操作
- `notepm_user_search` - ユーザー一覧の取得
- `notepm_user_detail` - ユーザー詳細の取得
- `notepm_user_me` - 自分のユーザー情報を取得

### グループ操作
- `notepm_group_search` - グループ一覧の取得
- `notepm_group_create` - グループの作成
- `notepm_group_detail` - グループ詳細の取得
- `notepm_group_delete` - グループの削除

## 必要条件

- Python 3.12以上
- NotePMのアカウントとAPI Token
- [uv](https://github.com/astral-sh/uv)

## インストール

```sh
uv sync
```

## 環境設定

以下の環境変数を設定する必要があります：

- `NOTEPM_TEAM`: NotePMのチーム名
- `NOTEPM_API_TOKEN`: NotePM APIトークン

`.env`ファイルを作成して設定することもできます：

```.env
NOTEPM_TEAM=your-team-name
NOTEPM_API_TOKEN=your-api-token
```

## 使用方法

### サーバーの起動

```bash
uv run notepm-mcp-server
```

### MCPクライアントの設定

```json
"servers": {
  "notepm-mcp-server": {
  "command": "uv",
    "args": [
      "--directory",
      "/<path to mcp-servers>/notepm-mcp-server",
      "run",
      "notepm-mcp-server"
    ],
    "env": {
      "NOTEPM_TEAM": "your-team-name",
      "NOTEPM_API_TOKEN": "your-api-token"
    }
  }
}
```

### Docker利用時のMCPクライアント設定

```json
{
  "mcpServers": {
    "notepm-mcp-server": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "NOTEPM_TEAM",
        "-e", "NOTEPM_API_TOKEN",
        "ghcr.io/dynamis-jp/notepm-mcp-server"
      ],
      "env": {
        "NOTEPM_TEAM": "your-team-name",
        "NOTEPM_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

## ツールの使用例

### ページ作成
```json
{
  "note_code": "abc123",
  "title": "新しいページ",
  "body": "ページの本文",
  "tags": ["タグ1", "タグ2"],
  "folder_id": 123
}
```

### ページ更新
```json
{
  "page_code": "xyz789",
  "title": "更新されたタイトル",
  "body": "更新された本文"
}
```

### ノート作成
```json
{
  "name": "新しいノート",
  "scope": "open",
  "description": "ノートの説明"
}
```

### フォルダ作成
```json
{
  "note_code": "abc123",
  "name": "新しいフォルダ",
  "parent_folder_id": 456
}
```

### コメント作成
```json
{
  "page_code": "xyz789",
  "body": "コメント本文",
  "notify_user_codes": ["user1", "user2"]
}
```

### タグ作成
```json
{
  "name": "新しいタグ",
  "parent_name": "親タグ"
}
```

### グループ作成
```json
{
  "name": "新しいグループ"
}
```

### 添付ファイルアップロード（ファイルパス指定）
```json
{
  "page_code": "xyz789",
  "file_name": "document.pdf",
  "file_path": "/path/to/document.pdf"
}
```

### 添付ファイルアップロード（Base64指定）
```json
{
  "page_code": "xyz789",
  "file_name": "image.png",
  "file_content_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
}
```

## 環境変数によるカスタマイズ

ツールの説明文を環境変数で上書きすることができます：

| 環境変数 | 説明 |
|---------|------|
| `NOTEPM_MAX_BODY_LENGTH` | 検索結果の本文最大文字数（デフォルト: 200） |
| `NOTEPM_SEARCH_DESCRIPTION` | 検索ツールの説明 |
| `NOTEPM_PAGE_DETAIL_DESCRIPTION` | ページ詳細取得ツールの説明 |
| `NOTEPM_PAGE_CREATE_DESCRIPTION` | ページ作成ツールの説明 |
| `NOTEPM_PAGE_UPDATE_DESCRIPTION` | ページ更新ツールの説明 |
| `NOTEPM_PAGE_DELETE_DESCRIPTION` | ページ削除ツールの説明 |
| `NOTEPM_NOTE_LIST_DESCRIPTION` | ノート一覧取得ツールの説明 |
| `NOTEPM_NOTE_DETAIL_DESCRIPTION` | ノート詳細取得ツールの説明 |
| `NOTEPM_NOTE_CREATE_DESCRIPTION` | ノート作成ツールの説明 |
| `NOTEPM_NOTE_UPDATE_DESCRIPTION` | ノート更新ツールの説明 |
| `NOTEPM_NOTE_DELETE_DESCRIPTION` | ノート削除ツールの説明 |
| `NOTEPM_NOTE_ARCHIVE_DESCRIPTION` | ノートアーカイブツールの説明 |
| `NOTEPM_NOTE_UNARCHIVE_DESCRIPTION` | ノートアーカイブ解除ツールの説明 |
| `NOTEPM_FOLDER_LIST_DESCRIPTION` | フォルダ一覧取得ツールの説明 |
| `NOTEPM_FOLDER_CREATE_DESCRIPTION` | フォルダ作成ツールの説明 |
| `NOTEPM_COMMENT_SEARCH_DESCRIPTION` | コメント検索ツールの説明 |
| `NOTEPM_COMMENT_CREATE_DESCRIPTION` | コメント作成ツールの説明 |
| `NOTEPM_COMMENT_UPDATE_DESCRIPTION` | コメント更新ツールの説明 |
| `NOTEPM_COMMENT_DELETE_DESCRIPTION` | コメント削除ツールの説明 |
| `NOTEPM_ATTACHMENT_SEARCH_DESCRIPTION` | 添付ファイル検索ツールの説明 |
| `NOTEPM_ATTACHMENT_DOWNLOAD_DESCRIPTION` | 添付ファイルダウンロードツールの説明 |
| `NOTEPM_ATTACHMENT_DELETE_DESCRIPTION` | 添付ファイル削除ツールの説明 |
| `NOTEPM_ATTACHMENT_UPLOAD_DESCRIPTION` | 添付ファイルアップロードツールの説明 |
| `NOTEPM_TAG_SEARCH_DESCRIPTION` | タグ検索ツールの説明 |
| `NOTEPM_TAG_CREATE_DESCRIPTION` | タグ作成ツールの説明 |
| `NOTEPM_TAG_DELETE_DESCRIPTION` | タグ削除ツールの説明 |
| `NOTEPM_USER_SEARCH_DESCRIPTION` | ユーザー検索ツールの説明 |
| `NOTEPM_USER_DETAIL_DESCRIPTION` | ユーザー詳細取得ツールの説明 |
| `NOTEPM_USER_ME_DESCRIPTION` | 自分のユーザー情報取得ツールの説明 |
| `NOTEPM_GROUP_SEARCH_DESCRIPTION` | グループ検索ツールの説明 |
| `NOTEPM_GROUP_CREATE_DESCRIPTION` | グループ作成ツールの説明 |
| `NOTEPM_GROUP_DETAIL_DESCRIPTION` | グループ詳細取得ツールの説明 |
| `NOTEPM_GROUP_DELETE_DESCRIPTION` | グループ削除ツールの説明 |
