from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import BaseModel
import httpx
import os
import base64
from typing import Optional
from dotenv import load_dotenv
import json

# 環境変数の読み込み
load_dotenv()


class NotePMConfig:
    """NotePM APIの設定を管理するクラス

    環境変数から必要な設定を読み込み、APIエンドポイントのURLを生成します。

    Attributes:
        team (str): NotePMのチーム名
        api_token (str): NotePM APIのトークン
        api_base (str): APIのベースURL
        max_body_length (int): 本文の最大文字数
    """

    def __init__(self):
        self.team = os.getenv("NOTEPM_TEAM")
        self.api_token = os.getenv("NOTEPM_API_TOKEN")
        if not self.team or not self.api_token:
            raise ValueError("環境変数NOTEPM_TEAMとNOTEPM_API_TOKENが必要です")
        self.api_base = f"https://{self.team}.notepm.jp/api/v1"

        # 本文の最大文字数を環境変数から取得（デフォルト: 200）
        self.max_body_length = int(os.getenv("NOTEPM_MAX_BODY_LENGTH", "200"))


class SearchParams(BaseModel):
    """NotePM API検索パラメータモデル

    Attributes:
        q (str): 検索クエリ
        only_title (int): タイトルのみを検索するかどうか (0: 全文検索, 1: タイトルのみ)
        include_archived (int): アーカイブされたページを含めるかどうか (0: 含めない, 1: 含める)
        note_code (Optional[str]): ノートコードによるフィルタリング
        tag_name (Optional[str]): タグ名によるフィルタリング
        created (Optional[str]): 作成日によるフィルタリング
        page (int): ページ番号 (デフォルト: 1)
        per_page (int): 1ページあたりの結果数 (デフォルト: 10)
    """

    q: str
    only_title: int = 0
    include_archived: int = 0
    note_code: Optional[str] = None
    tag_name: Optional[str] = None
    created: Optional[str] = None
    page: int = 1
    per_page: int = 10  # デフォルトを50から10に削減してレスポンスサイズを抑制


class NotePMDetailParams(BaseModel):
    """NotePM API詳細取得パラメータモデル

    Attributes:
        page_code (str): ページコード
    """

    page_code: str


# ページ作成パラメータ
class PageCreateParams(BaseModel):
    """ページ作成パラメータモデル

    Attributes:
        note_code (str): ノートコード（必須）
        title (str): ページタイトル（必須、最大100文字）
        folder_id (Optional[int]): フォルダID
        body (Optional[str]): ページ本文
        memo (Optional[str]): 変更履歴メモ（最大255文字）
        tags (Optional[list[str]]): タグ配列
        user (Optional[str]): ユーザーコードまたはユーザー名
        created_at (Optional[str]): 作成日時（ISO 8601形式）
    """

    note_code: str
    title: str
    folder_id: Optional[int] = None
    body: Optional[str] = None
    memo: Optional[str] = None
    tags: Optional[list[str]] = None
    user: Optional[str] = None
    created_at: Optional[str] = None


# ページ更新パラメータ
class PageUpdateParams(BaseModel):
    """ページ更新パラメータモデル

    Attributes:
        page_code (str): ページコード（必須）
        title (Optional[str]): ページタイトル（最大100文字）
        folder_id (Optional[int]): フォルダID
        body (Optional[str]): ページ本文
        memo (Optional[str]): 変更履歴メモ（最大255文字）
        tags (Optional[list[str]]): タグ配列
    """

    page_code: str
    title: Optional[str] = None
    folder_id: Optional[int] = None
    body: Optional[str] = None
    memo: Optional[str] = None
    tags: Optional[list[str]] = None


# ページ削除パラメータ
class PageDeleteParams(BaseModel):
    """ページ削除パラメータモデル

    Attributes:
        page_code (str): ページコード（必須）
    """

    page_code: str


# ノート一覧取得パラメータ
class NoteListParams(BaseModel):
    """ノート一覧取得パラメータモデル

    Attributes:
        page (int): ページ番号（デフォルト: 1）
        per_page (int): 1ページあたりの件数（デフォルト: 20、最大: 100）
    """

    page: int = 1
    per_page: int = 20


# ノート詳細取得パラメータ
class NoteDetailParams(BaseModel):
    """ノート詳細取得パラメータモデル

    Attributes:
        note_code (str): ノートコード（必須）
    """

    note_code: str


# ノート作成パラメータ
class NoteCreateParams(BaseModel):
    """ノート作成パラメータモデル

    Attributes:
        name (str): ノート名（必須、30文字以内）
        scope (str): 公開範囲（必須、"open"または"private"）
        icon (Optional[str]): アイコン（BASE64エンコード）
        description (Optional[str]): 説明（200文字以内）
        groups (Optional[list[str]]): グループコード配列
        users (Optional[list[str]]): ユーザーコード配列
    """

    name: str
    scope: str  # "open" or "private"
    icon: Optional[str] = None
    description: Optional[str] = None
    groups: Optional[list[str]] = None
    users: Optional[list[str]] = None


# ノート更新パラメータ
class NoteUpdateParams(BaseModel):
    """ノート更新パラメータモデル

    Attributes:
        note_code (str): ノートコード（必須）
        name (Optional[str]): ノート名（30文字以内）
        scope (Optional[str]): 公開範囲（"open"または"private"）
        description (Optional[str]): 説明（200文字以内）
        groups (Optional[list[str]]): グループコード配列
        users (Optional[list[str]]): ユーザーコード配列
    """

    note_code: str
    name: Optional[str] = None
    scope: Optional[str] = None
    description: Optional[str] = None
    groups: Optional[list[str]] = None
    users: Optional[list[str]] = None


# ノート削除パラメータ
class NoteDeleteParams(BaseModel):
    """ノート削除パラメータモデル

    Attributes:
        note_code (str): ノートコード（必須）
    """

    note_code: str


# フォルダ一覧取得パラメータ
class FolderListParams(BaseModel):
    """フォルダ一覧取得パラメータモデル

    Attributes:
        note_code (str): ノートコード（必須）
        include_archived (int): アーカイブを含めるか（0: 含めない, 1: 含める）
        page (int): ページ番号（デフォルト: 1）
        per_page (int): 1ページあたりの件数（デフォルト: 20、最大: 100）
    """

    note_code: str
    include_archived: int = 0
    page: int = 1
    per_page: int = 20


# フォルダ作成パラメータ
class FolderCreateParams(BaseModel):
    """フォルダ作成パラメータモデル

    Attributes:
        note_code (str): ノートコード（必須）
        name (str): フォルダ名（必須、最大100文字）
        parent_folder_id (Optional[int]): 親フォルダID（指定なしでノート直下に作成）
    """

    note_code: str
    name: str
    parent_folder_id: Optional[int] = None


# ノートアーカイブパラメータ
class NoteArchiveParams(BaseModel):
    """ノートアーカイブパラメータモデル"""
    note_code: str


# コメント検索パラメータ
class CommentSearchParams(BaseModel):
    """コメント検索パラメータモデル"""
    q: Optional[str] = None
    note_code: Optional[str] = None
    page_code: Optional[str] = None
    comment_by: Optional[str] = None
    page: int = 1
    per_page: int = 20


# コメント作成パラメータ
class CommentCreateParams(BaseModel):
    """コメント作成パラメータモデル"""
    page_code: str
    body: str
    user: Optional[str] = None
    created_at: Optional[str] = None
    notify_user_codes: Optional[list[str]] = None


# コメント更新パラメータ
class CommentUpdateParams(BaseModel):
    """コメント更新パラメータモデル"""
    page_code: str
    comment_number: int
    body: str


# コメント削除パラメータ
class CommentDeleteParams(BaseModel):
    """コメント削除パラメータモデル"""
    page_code: str
    comment_number: int


# 添付ファイル検索パラメータ
class AttachmentSearchParams(BaseModel):
    """添付ファイル検索パラメータモデル"""
    q: Optional[str] = None
    file_name: Optional[str] = None
    note_code: Optional[str] = None
    page_code: Optional[str] = None
    page: int = 1
    per_page: int = 20


# 添付ファイルダウンロードパラメータ
class AttachmentDownloadParams(BaseModel):
    """添付ファイルダウンロードパラメータモデル"""
    file_id: str


# 添付ファイル削除パラメータ
class AttachmentDeleteParams(BaseModel):
    """添付ファイル削除パラメータモデル"""
    file_id: str


# 添付ファイルアップロードパラメータ
class AttachmentUploadParams(BaseModel):
    """添付ファイルアップロードパラメータモデル

    Attributes:
        page_code (str): ファイルを添付するページのコード（必須）
        file_name (str): アップロードするファイルの名前（必須）
        file_path (Optional[str]): アップロードするファイルのパス（file_contentと排他）
        file_content_base64 (Optional[str]): Base64エンコードされたファイルコンテンツ（file_pathと排他）
        comment_number (Optional[int]): ファイルを添付するコメント番号
    """
    page_code: str
    file_name: str
    file_path: Optional[str] = None
    file_content_base64: Optional[str] = None
    comment_number: Optional[int] = None


# タグ検索パラメータ
class TagSearchParams(BaseModel):
    """タグ検索パラメータモデル"""
    page: int = 1
    per_page: int = 20


# タグ作成パラメータ
class TagCreateParams(BaseModel):
    """タグ作成パラメータモデル"""
    name: str
    parent_name: Optional[str] = None


# タグ削除パラメータ
class TagDeleteParams(BaseModel):
    """タグ削除パラメータモデル"""
    name: str


# ユーザー検索パラメータ
class UserSearchParams(BaseModel):
    """ユーザー検索パラメータモデル"""
    status: Optional[str] = None  # normal/deleted/suspended
    page: int = 1
    per_page: int = 20


# ユーザー詳細取得パラメータ
class UserDetailParams(BaseModel):
    """ユーザー詳細取得パラメータモデル"""
    user_code: str


# グループ検索パラメータ
class GroupSearchParams(BaseModel):
    """グループ検索パラメータモデル"""
    name: Optional[str] = None
    user_code: Optional[str] = None
    page: int = 1
    per_page: int = 20


# グループ作成パラメータ
class GroupCreateParams(BaseModel):
    """グループ作成パラメータモデル"""
    name: str


# グループ詳細取得パラメータ
class GroupDetailParams(BaseModel):
    """グループ詳細取得パラメータモデル"""
    group_name: str


# グループ削除パラメータ
class GroupDeleteParams(BaseModel):
    """グループ削除パラメータモデル"""
    group_name: str


class NotePMAPIClient:
    """NotePM APIクライアント

    非同期HTTPクライアントを使用してNotePM APIと通信を行います。
    コンテキストマネージャとして使用することで、リソースの適切な解放を保証します。
    """

    def __init__(self, config: NotePMConfig):
        """
        Args:
            config (NotePMConfig): API設定
        """
        self.config = config
        self._client = httpx.AsyncClient()

    async def __aenter__(self):
        """非同期コンテキストマネージャのエントリーポイント"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャの終了処理

        HTTPクライアントのリソースを適切に解放します。
        """
        await self._client.aclose()

    async def search(self, params: SearchParams) -> str:
        """NotePMの検索APIを呼び出します

        Args:
            params (SearchParams): 検索パラメータ

        Returns:
            str: 検索結果のJSON文字列

        Raises:
            ValueError: APIリクエストが失敗した場合
        """
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        response = await self._client.get(
            f"{self.config.api_base}/pages",
            params=params.dict(exclude_none=True),  # Noneの値を除外してパラメータを構築
            headers=headers,
        )

        if response.status_code != 200:
            raise ValueError(
                f"NotePM APIからのデータ取得に失敗しました: {response.status_code} {response.text}"
            )

        try:
            data = json.loads(response.text)
            # レスポンスの本文部分を設定された文字数で制限
            self._truncate_body_content(data, self.config.max_body_length)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}")
        return json.dumps(data, ensure_ascii=False)

    async def get_notepm_page_detail(self, params: NotePMDetailParams) -> str:
        """NotePMの詳細取得APIを呼び出します

        Args:
            params (NotePMDetailParams): 詳細取得パラメータ

        Returns:
            str: 詳細取得結果のJSON文字列

        Raises:
            ValueError: APIリクエストが失敗した場合
        """
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        url = f"{self.config.api_base}/pages/{params.page_code}"
        response = await self._client.get(url, headers=headers)

        if response.status_code != 200:
            raise ValueError(
                f"NotePM APIからのデータ取得に失敗しました: {response.status_code} {response.text}"
            )

        try:
            data = json.loads(response.text)
            # 詳細表示では本文を省略しない
            return json.dumps(data, ensure_ascii=False)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}")

    # ページ作成
    async def create_page(self, params: PageCreateParams) -> str:
        """ページを作成します

        Args:
            params (PageCreateParams): ページ作成パラメータ

        Returns:
            str: 作成結果のJSON文字列
        """
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        body = params.dict(exclude_none=True)
        body.pop("note_code", None)  # note_codeはbodyには含めない
        body["note_code"] = params.note_code  # note_codeはbodyに含める

        response = await self._client.post(
            f"{self.config.api_base}/pages",
            json=body,
            headers=headers,
        )

        if response.status_code not in [200, 201]:
            raise ValueError(
                f"ページの作成に失敗しました: {response.status_code} {response.text}"
            )

        return response.text

    # ページ更新
    async def update_page(self, params: PageUpdateParams) -> str:
        """ページを更新します

        Args:
            params (PageUpdateParams): ページ更新パラメータ

        Returns:
            str: 更新結果のJSON文字列
        """
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        body = params.dict(exclude_none=True)
        page_code = body.pop("page_code")

        response = await self._client.patch(
            f"{self.config.api_base}/pages/{page_code}",
            json=body,
            headers=headers,
        )

        if response.status_code != 200:
            raise ValueError(
                f"ページの更新に失敗しました: {response.status_code} {response.text}"
            )

        return response.text

    # ページ削除
    async def delete_page(self, params: PageDeleteParams) -> str:
        """ページを削除します

        Args:
            params (PageDeleteParams): ページ削除パラメータ

        Returns:
            str: 削除結果メッセージ
        """
        headers = {"Authorization": f"Bearer {self.config.api_token}"}

        response = await self._client.delete(
            f"{self.config.api_base}/pages/{params.page_code}",
            headers=headers,
        )

        if response.status_code != 204:
            raise ValueError(
                f"ページの削除に失敗しました: {response.status_code} {response.text}"
            )

        return json.dumps({"message": "ページを削除しました", "page_code": params.page_code}, ensure_ascii=False)

    # ノート一覧取得
    async def list_notes(self, params: NoteListParams) -> str:
        """ノート一覧を取得します

        Args:
            params (NoteListParams): ノート一覧取得パラメータ

        Returns:
            str: ノート一覧のJSON文字列
        """
        headers = {"Authorization": f"Bearer {self.config.api_token}"}

        response = await self._client.get(
            f"{self.config.api_base}/notes",
            params=params.dict(exclude_none=True),
            headers=headers,
        )

        if response.status_code != 200:
            raise ValueError(
                f"ノート一覧の取得に失敗しました: {response.status_code} {response.text}"
            )

        return response.text

    # ノート詳細取得
    async def get_note_detail(self, params: NoteDetailParams) -> str:
        """ノート詳細を取得します

        Args:
            params (NoteDetailParams): ノート詳細取得パラメータ

        Returns:
            str: ノート詳細のJSON文字列
        """
        headers = {"Authorization": f"Bearer {self.config.api_token}"}

        response = await self._client.get(
            f"{self.config.api_base}/notes/{params.note_code}",
            headers=headers,
        )

        if response.status_code != 200:
            raise ValueError(
                f"ノート詳細の取得に失敗しました: {response.status_code} {response.text}"
            )

        return response.text

    # ノート作成
    async def create_note(self, params: NoteCreateParams) -> str:
        """ノートを作成します

        Args:
            params (NoteCreateParams): ノート作成パラメータ

        Returns:
            str: 作成結果のJSON文字列
        """
        headers = {"Authorization": f"Bearer {self.config.api_token}"}

        response = await self._client.post(
            f"{self.config.api_base}/notes",
            json=params.dict(exclude_none=True),
            headers=headers,
        )

        if response.status_code not in [200, 201]:
            raise ValueError(
                f"ノートの作成に失敗しました: {response.status_code} {response.text}"
            )

        return response.text

    # ノート更新
    async def update_note(self, params: NoteUpdateParams) -> str:
        """ノートを更新します

        Args:
            params (NoteUpdateParams): ノート更新パラメータ

        Returns:
            str: 更新結果のJSON文字列
        """
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        body = params.dict(exclude_none=True)
        note_code = body.pop("note_code")

        response = await self._client.patch(
            f"{self.config.api_base}/notes/{note_code}",
            json=body,
            headers=headers,
        )

        if response.status_code != 200:
            raise ValueError(
                f"ノートの更新に失敗しました: {response.status_code} {response.text}"
            )

        return response.text

    # ノート削除
    async def delete_note(self, params: NoteDeleteParams) -> str:
        """ノートを削除します

        Args:
            params (NoteDeleteParams): ノート削除パラメータ

        Returns:
            str: 削除結果メッセージ
        """
        headers = {"Authorization": f"Bearer {self.config.api_token}"}

        response = await self._client.delete(
            f"{self.config.api_base}/notes/{params.note_code}",
            headers=headers,
        )

        if response.status_code != 204:
            raise ValueError(
                f"ノートの削除に失敗しました: {response.status_code} {response.text}"
            )

        return json.dumps({"message": "ノートを削除しました", "note_code": params.note_code}, ensure_ascii=False)

    # フォルダ一覧取得
    async def list_folders(self, params: FolderListParams) -> str:
        """フォルダ一覧を取得します

        Args:
            params (FolderListParams): フォルダ一覧取得パラメータ

        Returns:
            str: フォルダ一覧のJSON文字列
        """
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        query_params = params.dict(exclude_none=True)
        note_code = query_params.pop("note_code")

        response = await self._client.get(
            f"{self.config.api_base}/notes/{note_code}/folders",
            params=query_params,
            headers=headers,
        )

        if response.status_code != 200:
            raise ValueError(
                f"フォルダ一覧の取得に失敗しました: {response.status_code} {response.text}"
            )

        return response.text

    # フォルダ作成
    async def create_folder(self, params: FolderCreateParams) -> str:
        """フォルダを作成します

        Args:
            params (FolderCreateParams): フォルダ作成パラメータ

        Returns:
            str: 作成結果のJSON文字列
        """
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        body = params.dict(exclude_none=True)
        note_code = body.pop("note_code")

        response = await self._client.post(
            f"{self.config.api_base}/notes/{note_code}/folders",
            json=body,
            headers=headers,
        )

        if response.status_code not in [200, 201]:
            raise ValueError(
                f"フォルダの作成に失敗しました: {response.status_code} {response.text}"
            )

        return response.text

    # ノートアーカイブ
    async def archive_note(self, params: NoteArchiveParams) -> str:
        """ノートをアーカイブします"""
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        response = await self._client.patch(
            f"{self.config.api_base}/notes/{params.note_code}/archive",
            headers=headers,
        )
        if response.status_code not in [200, 204]:
            raise ValueError(f"ノートのアーカイブに失敗しました: {response.status_code} {response.text}")
        if response.status_code == 204:
            return json.dumps({"message": "ノートをアーカイブしました", "note_code": params.note_code}, ensure_ascii=False)
        return response.text

    # ノートアーカイブ解除
    async def unarchive_note(self, params: NoteArchiveParams) -> str:
        """ノートのアーカイブを解除します"""
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        response = await self._client.patch(
            f"{self.config.api_base}/notes/{params.note_code}/extract",
            headers=headers,
        )
        if response.status_code not in [200, 204]:
            raise ValueError(f"ノートのアーカイブ解除に失敗しました: {response.status_code} {response.text}")
        if response.status_code == 204:
            return json.dumps({"message": "ノートのアーカイブを解除しました", "note_code": params.note_code}, ensure_ascii=False)
        return response.text

    # コメント検索
    async def search_comments(self, params: CommentSearchParams) -> str:
        """コメントを検索します"""
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        response = await self._client.get(
            f"{self.config.api_base}/comments",
            params=params.dict(exclude_none=True),
            headers=headers,
        )
        if response.status_code != 200:
            raise ValueError(f"コメントの検索に失敗しました: {response.status_code} {response.text}")
        return response.text

    # コメント作成
    async def create_comment(self, params: CommentCreateParams) -> str:
        """コメントを作成します"""
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        body = params.dict(exclude_none=True)
        page_code = body.pop("page_code")
        response = await self._client.post(
            f"{self.config.api_base}/pages/{page_code}/comments",
            json=body,
            headers=headers,
        )
        if response.status_code not in [200, 201]:
            raise ValueError(f"コメントの作成に失敗しました: {response.status_code} {response.text}")
        return response.text

    # コメント更新
    async def update_comment(self, params: CommentUpdateParams) -> str:
        """コメントを更新します"""
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        response = await self._client.patch(
            f"{self.config.api_base}/pages/{params.page_code}/comments/{params.comment_number}",
            json={"body": params.body},
            headers=headers,
        )
        if response.status_code != 200:
            raise ValueError(f"コメントの更新に失敗しました: {response.status_code} {response.text}")
        return response.text

    # コメント削除
    async def delete_comment(self, params: CommentDeleteParams) -> str:
        """コメントを削除します"""
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        response = await self._client.delete(
            f"{self.config.api_base}/pages/{params.page_code}/comments/{params.comment_number}",
            headers=headers,
        )
        if response.status_code != 204:
            raise ValueError(f"コメントの削除に失敗しました: {response.status_code} {response.text}")
        return json.dumps({"message": "コメントを削除しました"}, ensure_ascii=False)

    # 添付ファイル検索
    async def search_attachments(self, params: AttachmentSearchParams) -> str:
        """添付ファイルを検索します"""
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        response = await self._client.get(
            f"{self.config.api_base}/attachments",
            params=params.dict(exclude_none=True),
            headers=headers,
        )
        if response.status_code != 200:
            raise ValueError(f"添付ファイルの検索に失敗しました: {response.status_code} {response.text}")
        return response.text

    # 添付ファイルダウンロード情報取得
    async def get_attachment_download_url(self, params: AttachmentDownloadParams) -> str:
        """添付ファイルのダウンロードURLを取得します"""
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        response = await self._client.get(
            f"{self.config.api_base}/attachments/download/{params.file_id}",
            headers=headers,
            follow_redirects=False,
        )
        if response.status_code in [200, 302]:
            return json.dumps({
                "file_id": params.file_id,
                "download_url": f"{self.config.api_base}/attachments/download/{params.file_id}",
                "message": "Bearer認証ヘッダーを付けてこのURLにアクセスしてください"
            }, ensure_ascii=False)
        raise ValueError(f"添付ファイルのダウンロードに失敗しました: {response.status_code} {response.text}")

    # 添付ファイル削除
    async def delete_attachment(self, params: AttachmentDeleteParams) -> str:
        """添付ファイルを削除します"""
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        response = await self._client.delete(
            f"{self.config.api_base}/attachments/{params.file_id}",
            headers=headers,
        )
        if response.status_code != 204:
            raise ValueError(f"添付ファイルの削除に失敗しました: {response.status_code} {response.text}")
        return json.dumps({"message": "添付ファイルを削除しました", "file_id": params.file_id}, ensure_ascii=False)

    # 添付ファイルアップロード
    async def upload_attachment(self, params: AttachmentUploadParams) -> str:
        """添付ファイルをアップロードします

        file_pathまたはfile_content_base64のいずれかを指定する必要があります。
        両方指定された場合はfile_pathが優先されます。
        """
        headers = {"Authorization": f"Bearer {self.config.api_token}"}

        # ファイルコンテンツの取得
        if params.file_path:
            # ファイルパスから読み込み
            if not os.path.exists(params.file_path):
                raise ValueError(f"ファイルが見つかりません: {params.file_path}")
            with open(params.file_path, "rb") as f:
                file_content = f.read()
        elif params.file_content_base64:
            # Base64デコード
            try:
                file_content = base64.b64decode(params.file_content_base64)
            except Exception as e:
                raise ValueError(f"Base64デコードに失敗しました: {e}")
        else:
            raise ValueError("file_pathまたはfile_content_base64のいずれかを指定してください")

        # multipart/form-dataの構築
        files = {
            "file[name]": (None, params.file_name),
            "file[contents]": (params.file_name, file_content),
        }
        data = {
            "page_code": params.page_code,
        }
        if params.comment_number is not None:
            data["comment_number"] = str(params.comment_number)

        response = await self._client.post(
            f"{self.config.api_base}/attachments",
            headers=headers,
            files=files,
            data=data,
        )

        if response.status_code not in [200, 201]:
            raise ValueError(f"添付ファイルのアップロードに失敗しました: {response.status_code} {response.text}")

        return response.text

    # タグ検索
    async def search_tags(self, params: TagSearchParams) -> str:
        """タグを検索します"""
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        response = await self._client.get(
            f"{self.config.api_base}/tags",
            params=params.dict(exclude_none=True),
            headers=headers,
        )
        if response.status_code != 200:
            raise ValueError(f"タグの検索に失敗しました: {response.status_code} {response.text}")
        return response.text

    # タグ作成
    async def create_tag(self, params: TagCreateParams) -> str:
        """タグを作成します"""
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        response = await self._client.post(
            f"{self.config.api_base}/tags",
            json=params.dict(exclude_none=True),
            headers=headers,
        )
        if response.status_code not in [200, 201]:
            raise ValueError(f"タグの作成に失敗しました: {response.status_code} {response.text}")
        return response.text

    # タグ削除
    async def delete_tag(self, params: TagDeleteParams) -> str:
        """タグを削除します"""
        headers = {
            "Authorization": f"Bearer {self.config.api_token}",
            "Content-Type": "application/json"
        }
        response = await self._client.request(
            "DELETE",
            f"{self.config.api_base}/tags",
            headers=headers,
            content=json.dumps({"name": params.name}),
        )
        if response.status_code != 204:
            raise ValueError(f"タグの削除に失敗しました: {response.status_code} {response.text}")
        return json.dumps({"message": "タグを削除しました", "name": params.name}, ensure_ascii=False)

    # ユーザー検索
    async def search_users(self, params: UserSearchParams) -> str:
        """ユーザーを検索します"""
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        response = await self._client.get(
            f"{self.config.api_base}/users",
            params=params.dict(exclude_none=True),
            headers=headers,
        )
        if response.status_code != 200:
            raise ValueError(f"ユーザーの検索に失敗しました: {response.status_code} {response.text}")
        return response.text

    # ユーザー詳細取得
    async def get_user_detail(self, params: UserDetailParams) -> str:
        """ユーザー詳細を取得します"""
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        response = await self._client.get(
            f"{self.config.api_base}/users/{params.user_code}",
            headers=headers,
        )
        if response.status_code != 200:
            raise ValueError(f"ユーザー詳細の取得に失敗しました: {response.status_code} {response.text}")
        return response.text

    # 自分のユーザー情報取得
    async def get_my_account(self) -> str:
        """自分のユーザー情報を取得します"""
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        response = await self._client.get(
            f"{self.config.api_base}/user/account",
            headers=headers,
        )
        if response.status_code != 200:
            raise ValueError(f"自分のユーザー情報の取得に失敗しました: {response.status_code} {response.text}")
        return response.text

    # グループ検索
    async def search_groups(self, params: GroupSearchParams) -> str:
        """グループを検索します"""
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        response = await self._client.get(
            f"{self.config.api_base}/groups",
            params=params.dict(exclude_none=True),
            headers=headers,
        )
        if response.status_code != 200:
            raise ValueError(f"グループの検索に失敗しました: {response.status_code} {response.text}")
        return response.text

    # グループ作成
    async def create_group(self, params: GroupCreateParams) -> str:
        """グループを作成します"""
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        response = await self._client.post(
            f"{self.config.api_base}/groups",
            json=params.dict(exclude_none=True),
            headers=headers,
        )
        if response.status_code not in [200, 201]:
            raise ValueError(f"グループの作成に失敗しました: {response.status_code} {response.text}")
        return response.text

    # グループ詳細取得
    async def get_group_detail(self, params: GroupDetailParams) -> str:
        """グループ詳細を取得します"""
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        response = await self._client.get(
            f"{self.config.api_base}/groups/{params.group_name}",
            headers=headers,
        )
        if response.status_code != 200:
            raise ValueError(f"グループ詳細の取得に失敗しました: {response.status_code} {response.text}")
        return response.text

    # グループ削除
    async def delete_group(self, params: GroupDeleteParams) -> str:
        """グループを削除します"""
        headers = {"Authorization": f"Bearer {self.config.api_token}"}
        response = await self._client.delete(
            f"{self.config.api_base}/groups/{params.group_name}",
            headers=headers,
        )
        if response.status_code != 204:
            raise ValueError(f"グループの削除に失敗しました: {response.status_code} {response.text}")
        return json.dumps({"message": "グループを削除しました", "group_name": params.group_name}, ensure_ascii=False)

    def _truncate_body_content(self, data: dict, max_length: int = 1000) -> None:
        """レスポンスデータの本文部分を指定された文字数で省略します

        Args:
            data (dict): NotePM APIのレスポンスデータ
            max_length (int): 本文の最大文字数 (デフォルト: 1000)
        """

        if isinstance(data, dict):
            # 検索結果の場合（pagesフィールドが存在する場合）
            if "pages" in data and isinstance(data["pages"], list):
                for page in data["pages"]:
                    if isinstance(page, dict) and "body" in page:
                        original_body = page["body"]

                        if (
                            isinstance(original_body, str)
                            and len(original_body) > max_length
                        ):
                            page["body"] = original_body[:max_length] + "..."

            # 詳細取得結果の場合（pageフィールドが存在する場合）
            elif "page" in data and isinstance(data["page"], dict):
                page = data["page"]
                if "body" in page:
                    original_body = page["body"]

                    if (
                        isinstance(original_body, str)
                        and len(original_body) > max_length
                    ):
                        page["body"] = original_body[:max_length] + "..."


def get_tool_description(env_var_name: str, default_description: str) -> str:
    """環境変数からツールの説明を取得する

    Args:
        env_var_name (str): 環境変数の名前
        default_description (str): デフォルトの説明文

    Returns:
        str: 環境変数から取得した説明文、または環境変数が設定されていない場合はデフォルトの説明文
    """
    return os.getenv(env_var_name, default_description)

async def serve() -> None:
    """MCPサーバーのメインエントリーポイント

    NotePM検索機能を提供するMCPサーバーを起動し、標準入出力を使用して
    他のプロセスとコマンド通信を行います。
    """
    config = NotePMConfig()
    server: Server = Server("notepm-mcp")

    # ツールの説明文のデフォルト値
    default_search_description = """
                    NotePM(ノートPM)で指定されたクエリを検索します。
                    検索ワードは単語のAND検索です。自然言語での検索はサポートされていません。
                    検索結果はJSON形式で返されます。
                    記事の本文が長い場合は、本文の全文が返されないことがあります。
                    全文を取得するには、notepm_page_detailを使用してください。
                """

    default_detail_description = "NotePM(ノートPM)で指定されたページコードの記事に対して詳細な内容を取得します。"

    default_page_create_description = "NotePM(ノートPM)で新しいページを作成します。note_codeとtitleは必須です。"
    default_page_update_description = "NotePM(ノートPM)で指定されたページを更新します。page_codeは必須です。"
    default_page_delete_description = "NotePM(ノートPM)で指定されたページを削除します。page_codeは必須です。"

    default_note_list_description = "NotePM(ノートPM)でノート一覧を取得します。"
    default_note_detail_description = "NotePM(ノートPM)で指定されたノートの詳細を取得します。"
    default_note_create_description = "NotePM(ノートPM)で新しいノートを作成します。nameとscope(open/private)は必須です。"
    default_note_update_description = "NotePM(ノートPM)で指定されたノートを更新します。note_codeは必須です。"
    default_note_delete_description = "NotePM(ノートPM)で指定されたノートを削除します。note_codeは必須です。"

    default_folder_list_description = "NotePM(ノートPM)で指定されたノート内のフォルダ一覧を取得します。"
    default_folder_create_description = "NotePM(ノートPM)で指定されたノート内に新しいフォルダを作成します。note_codeとnameは必須です。"

    default_note_archive_description = "NotePM(ノートPM)で指定されたノートをアーカイブします。"
    default_note_unarchive_description = "NotePM(ノートPM)で指定されたノートのアーカイブを解除します。"

    default_comment_search_description = "NotePM(ノートPM)でコメントを検索します。"
    default_comment_create_description = "NotePM(ノートPM)で指定されたページにコメントを作成します。page_codeとbodyは必須です。"
    default_comment_update_description = "NotePM(ノートPM)で指定されたコメントを更新します。"
    default_comment_delete_description = "NotePM(ノートPM)で指定されたコメントを削除します。"

    default_attachment_search_description = "NotePM(ノートPM)で添付ファイルを検索します。"
    default_attachment_download_description = "NotePM(ノートPM)で添付ファイルのダウンロード情報を取得します。"
    default_attachment_delete_description = "NotePM(ノートPM)で指定された添付ファイルを削除します。"
    default_attachment_upload_description = "NotePM(ノートPM)でページに添付ファイルをアップロードします。page_code、file_nameは必須。file_path（ファイルパス）またはfile_content_base64（Base64エンコードされたコンテンツ）のいずれかを指定してください。"

    default_tag_search_description = "NotePM(ノートPM)でタグ一覧を取得します。"
    default_tag_create_description = "NotePM(ノートPM)で新しいタグを作成します。nameは必須です。"
    default_tag_delete_description = "NotePM(ノートPM)で指定されたタグを削除します。"

    default_user_search_description = "NotePM(ノートPM)でユーザー一覧を取得します。"
    default_user_detail_description = "NotePM(ノートPM)で指定されたユーザーの詳細を取得します。"
    default_user_me_description = "NotePM(ノートPM)で自分のユーザー情報を取得します。"

    default_group_search_description = "NotePM(ノートPM)でグループ一覧を取得します。"
    default_group_create_description = "NotePM(ノートPM)で新しいグループを作成します。nameは必須です。"
    default_group_detail_description = "NotePM(ノートPM)で指定されたグループの詳細を取得します。"
    default_group_delete_description = "NotePM(ノートPM)で指定されたグループを削除します。"

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """利用可能なツールのリストを返します"""
        return [
            # ページ関連
            Tool(
                name="notepm_search",
                description=get_tool_description("NOTEPM_SEARCH_DESCRIPTION", default_search_description),
                inputSchema=SearchParams.schema(),
            ),
            Tool(
                name="notepm_page_detail",
                description=get_tool_description("NOTEPM_PAGE_DETAIL_DESCRIPTION", default_detail_description),
                inputSchema=NotePMDetailParams.schema(),
            ),
            Tool(
                name="notepm_page_create",
                description=get_tool_description("NOTEPM_PAGE_CREATE_DESCRIPTION", default_page_create_description),
                inputSchema=PageCreateParams.schema(),
            ),
            Tool(
                name="notepm_page_update",
                description=get_tool_description("NOTEPM_PAGE_UPDATE_DESCRIPTION", default_page_update_description),
                inputSchema=PageUpdateParams.schema(),
            ),
            Tool(
                name="notepm_page_delete",
                description=get_tool_description("NOTEPM_PAGE_DELETE_DESCRIPTION", default_page_delete_description),
                inputSchema=PageDeleteParams.schema(),
            ),
            # ノート関連
            Tool(
                name="notepm_note_list",
                description=get_tool_description("NOTEPM_NOTE_LIST_DESCRIPTION", default_note_list_description),
                inputSchema=NoteListParams.schema(),
            ),
            Tool(
                name="notepm_note_detail",
                description=get_tool_description("NOTEPM_NOTE_DETAIL_DESCRIPTION", default_note_detail_description),
                inputSchema=NoteDetailParams.schema(),
            ),
            Tool(
                name="notepm_note_create",
                description=get_tool_description("NOTEPM_NOTE_CREATE_DESCRIPTION", default_note_create_description),
                inputSchema=NoteCreateParams.schema(),
            ),
            Tool(
                name="notepm_note_update",
                description=get_tool_description("NOTEPM_NOTE_UPDATE_DESCRIPTION", default_note_update_description),
                inputSchema=NoteUpdateParams.schema(),
            ),
            Tool(
                name="notepm_note_delete",
                description=get_tool_description("NOTEPM_NOTE_DELETE_DESCRIPTION", default_note_delete_description),
                inputSchema=NoteDeleteParams.schema(),
            ),
            # フォルダ関連
            Tool(
                name="notepm_folder_list",
                description=get_tool_description("NOTEPM_FOLDER_LIST_DESCRIPTION", default_folder_list_description),
                inputSchema=FolderListParams.schema(),
            ),
            Tool(
                name="notepm_folder_create",
                description=get_tool_description("NOTEPM_FOLDER_CREATE_DESCRIPTION", default_folder_create_description),
                inputSchema=FolderCreateParams.schema(),
            ),
            # ノートアーカイブ関連
            Tool(
                name="notepm_note_archive",
                description=get_tool_description("NOTEPM_NOTE_ARCHIVE_DESCRIPTION", default_note_archive_description),
                inputSchema=NoteArchiveParams.schema(),
            ),
            Tool(
                name="notepm_note_unarchive",
                description=get_tool_description("NOTEPM_NOTE_UNARCHIVE_DESCRIPTION", default_note_unarchive_description),
                inputSchema=NoteArchiveParams.schema(),
            ),
            # コメント関連
            Tool(
                name="notepm_comment_search",
                description=get_tool_description("NOTEPM_COMMENT_SEARCH_DESCRIPTION", default_comment_search_description),
                inputSchema=CommentSearchParams.schema(),
            ),
            Tool(
                name="notepm_comment_create",
                description=get_tool_description("NOTEPM_COMMENT_CREATE_DESCRIPTION", default_comment_create_description),
                inputSchema=CommentCreateParams.schema(),
            ),
            Tool(
                name="notepm_comment_update",
                description=get_tool_description("NOTEPM_COMMENT_UPDATE_DESCRIPTION", default_comment_update_description),
                inputSchema=CommentUpdateParams.schema(),
            ),
            Tool(
                name="notepm_comment_delete",
                description=get_tool_description("NOTEPM_COMMENT_DELETE_DESCRIPTION", default_comment_delete_description),
                inputSchema=CommentDeleteParams.schema(),
            ),
            # 添付ファイル関連
            Tool(
                name="notepm_attachment_search",
                description=get_tool_description("NOTEPM_ATTACHMENT_SEARCH_DESCRIPTION", default_attachment_search_description),
                inputSchema=AttachmentSearchParams.schema(),
            ),
            Tool(
                name="notepm_attachment_download",
                description=get_tool_description("NOTEPM_ATTACHMENT_DOWNLOAD_DESCRIPTION", default_attachment_download_description),
                inputSchema=AttachmentDownloadParams.schema(),
            ),
            Tool(
                name="notepm_attachment_delete",
                description=get_tool_description("NOTEPM_ATTACHMENT_DELETE_DESCRIPTION", default_attachment_delete_description),
                inputSchema=AttachmentDeleteParams.schema(),
            ),
            Tool(
                name="notepm_attachment_upload",
                description=get_tool_description("NOTEPM_ATTACHMENT_UPLOAD_DESCRIPTION", default_attachment_upload_description),
                inputSchema=AttachmentUploadParams.schema(),
            ),
            # タグ関連
            Tool(
                name="notepm_tag_search",
                description=get_tool_description("NOTEPM_TAG_SEARCH_DESCRIPTION", default_tag_search_description),
                inputSchema=TagSearchParams.schema(),
            ),
            Tool(
                name="notepm_tag_create",
                description=get_tool_description("NOTEPM_TAG_CREATE_DESCRIPTION", default_tag_create_description),
                inputSchema=TagCreateParams.schema(),
            ),
            Tool(
                name="notepm_tag_delete",
                description=get_tool_description("NOTEPM_TAG_DELETE_DESCRIPTION", default_tag_delete_description),
                inputSchema=TagDeleteParams.schema(),
            ),
            # ユーザー関連
            Tool(
                name="notepm_user_search",
                description=get_tool_description("NOTEPM_USER_SEARCH_DESCRIPTION", default_user_search_description),
                inputSchema=UserSearchParams.schema(),
            ),
            Tool(
                name="notepm_user_detail",
                description=get_tool_description("NOTEPM_USER_DETAIL_DESCRIPTION", default_user_detail_description),
                inputSchema=UserDetailParams.schema(),
            ),
            Tool(
                name="notepm_user_me",
                description=get_tool_description("NOTEPM_USER_ME_DESCRIPTION", default_user_me_description),
                inputSchema={},
            ),
            # グループ関連
            Tool(
                name="notepm_group_search",
                description=get_tool_description("NOTEPM_GROUP_SEARCH_DESCRIPTION", default_group_search_description),
                inputSchema=GroupSearchParams.schema(),
            ),
            Tool(
                name="notepm_group_create",
                description=get_tool_description("NOTEPM_GROUP_CREATE_DESCRIPTION", default_group_create_description),
                inputSchema=GroupCreateParams.schema(),
            ),
            Tool(
                name="notepm_group_detail",
                description=get_tool_description("NOTEPM_GROUP_DETAIL_DESCRIPTION", default_group_detail_description),
                inputSchema=GroupDetailParams.schema(),
            ),
            Tool(
                name="notepm_group_delete",
                description=get_tool_description("NOTEPM_GROUP_DELETE_DESCRIPTION", default_group_delete_description),
                inputSchema=GroupDeleteParams.schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """クライアントからのツール呼び出しを処理します

        Args:
            name (str): 呼び出すツールの名前
            arguments (dict): ツールに渡す引数

        Returns:
            list[TextContent]: ツールの実行結果

        Raises:
            ValueError: 不明なツールが指定された場合
        """
        async with NotePMAPIClient(config) as client:
            # ページ関連
            if name == "notepm_search":
                params = SearchParams(**arguments)
                result = await client.search(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_page_detail":
                params = NotePMDetailParams(**arguments)
                result = await client.get_notepm_page_detail(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_page_create":
                params = PageCreateParams(**arguments)
                result = await client.create_page(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_page_update":
                params = PageUpdateParams(**arguments)
                result = await client.update_page(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_page_delete":
                params = PageDeleteParams(**arguments)
                result = await client.delete_page(params)
                return [TextContent(type="text", text=result)]
            # ノート関連
            elif name == "notepm_note_list":
                params = NoteListParams(**arguments)
                result = await client.list_notes(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_note_detail":
                params = NoteDetailParams(**arguments)
                result = await client.get_note_detail(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_note_create":
                params = NoteCreateParams(**arguments)
                result = await client.create_note(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_note_update":
                params = NoteUpdateParams(**arguments)
                result = await client.update_note(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_note_delete":
                params = NoteDeleteParams(**arguments)
                result = await client.delete_note(params)
                return [TextContent(type="text", text=result)]
            # フォルダ関連
            elif name == "notepm_folder_list":
                params = FolderListParams(**arguments)
                result = await client.list_folders(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_folder_create":
                params = FolderCreateParams(**arguments)
                result = await client.create_folder(params)
                return [TextContent(type="text", text=result)]
            # ノートアーカイブ関連
            elif name == "notepm_note_archive":
                params = NoteArchiveParams(**arguments)
                result = await client.archive_note(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_note_unarchive":
                params = NoteArchiveParams(**arguments)
                result = await client.unarchive_note(params)
                return [TextContent(type="text", text=result)]
            # コメント関連
            elif name == "notepm_comment_search":
                params = CommentSearchParams(**arguments)
                result = await client.search_comments(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_comment_create":
                params = CommentCreateParams(**arguments)
                result = await client.create_comment(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_comment_update":
                params = CommentUpdateParams(**arguments)
                result = await client.update_comment(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_comment_delete":
                params = CommentDeleteParams(**arguments)
                result = await client.delete_comment(params)
                return [TextContent(type="text", text=result)]
            # 添付ファイル関連
            elif name == "notepm_attachment_search":
                params = AttachmentSearchParams(**arguments)
                result = await client.search_attachments(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_attachment_download":
                params = AttachmentDownloadParams(**arguments)
                result = await client.get_attachment_download_url(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_attachment_delete":
                params = AttachmentDeleteParams(**arguments)
                result = await client.delete_attachment(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_attachment_upload":
                params = AttachmentUploadParams(**arguments)
                result = await client.upload_attachment(params)
                return [TextContent(type="text", text=result)]
            # タグ関連
            elif name == "notepm_tag_search":
                params = TagSearchParams(**arguments)
                result = await client.search_tags(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_tag_create":
                params = TagCreateParams(**arguments)
                result = await client.create_tag(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_tag_delete":
                params = TagDeleteParams(**arguments)
                result = await client.delete_tag(params)
                return [TextContent(type="text", text=result)]
            # ユーザー関連
            elif name == "notepm_user_search":
                params = UserSearchParams(**arguments)
                result = await client.search_users(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_user_detail":
                params = UserDetailParams(**arguments)
                result = await client.get_user_detail(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_user_me":
                result = await client.get_my_account()
                return [TextContent(type="text", text=result)]
            # グループ関連
            elif name == "notepm_group_search":
                params = GroupSearchParams(**arguments)
                result = await client.search_groups(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_group_create":
                params = GroupCreateParams(**arguments)
                result = await client.create_group(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_group_detail":
                params = GroupDetailParams(**arguments)
                result = await client.get_group_detail(params)
                return [TextContent(type="text", text=result)]
            elif name == "notepm_group_delete":
                params = GroupDeleteParams(**arguments)
                result = await client.delete_group(params)
                return [TextContent(type="text", text=result)]

        raise ValueError(f"不明なツールです: {name}")

    # サーバーの初期化オプションを作成
    options = server.create_initialization_options()
    # 標準入出力を使用してサーバーを起動
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
