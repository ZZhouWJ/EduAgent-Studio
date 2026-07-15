"""
课程知识库 Service 层。

处理文件上传、文档解析、chunk 生成的业务逻辑。
"""

import hashlib
import logging
import os
import zipfile
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.config import get_settings
from app.repositories.knowledge_repo import KnowledgeRepository
from app.repositories.evidence_repo import EvidenceRepository
from app.rag.parser import extract_bm25_terms, parse_document_file

logger = logging.getLogger(__name__)
MAX_MATERIAL_SIZE = 20 * 1024 * 1024


def validate_material_upload(
    file_content: bytes,
    filename: str,
    file_type: str,
) -> str:
    """校验上传边界、真实文件格式并返回安全文件名。"""
    if not file_content:
        raise ValueError("文件不能为空")
    if len(file_content) > MAX_MATERIAL_SIZE:
        raise ValueError("文件不能超过 20MB")

    safe_name = os.path.basename(filename.replace("\\", "/")).strip()
    if not safe_name or safe_name in {".", ".."}:
        raise ValueError("文件名无效")

    normalized_type = file_type.lower()
    if normalized_type == "pdf" and not file_content.startswith(b"%PDF-"):
        raise ValueError("PDF 文件内容与扩展名不一致")
    if normalized_type in {"word", "ppt"}:
        try:
            from io import BytesIO

            with zipfile.ZipFile(BytesIO(file_content)) as archive:
                names = set(archive.namelist())
        except zipfile.BadZipFile as exc:
            raise ValueError("Office 文件已损坏或格式不正确") from exc
        expected_entry = "word/document.xml" if normalized_type == "word" else "ppt/presentation.xml"
        if expected_entry not in names:
            raise ValueError("Office 文件内容与扩展名不一致")
    if normalized_type in {"markdown", "md", "text", "txt"}:
        if b"\x00" in file_content:
            raise ValueError("文本文件包含无效二进制内容")
        try:
            file_content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("文本文件必须使用 UTF-8 编码") from exc

    return safe_name


class KnowledgeService:
    """课程知识库服务层。"""

    def __init__(self) -> None:
        self._repo = KnowledgeRepository()
        self._evidence_repo = EvidenceRepository()
        self._settings = get_settings()

    def _get_upload_dir(self) -> str:
        """获取文件上传目录。"""
        upload_dir = os.path.join(self._settings.app_data_dir, "materials")
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

    def upload_material(
        self,
        course_id: int,
        file_content: bytes,
        filename: str,
        file_type: str,
        created_by: int,
    ) -> Dict[str, Any]:
        """
        上传课程资料文件。

        Args:
            course_id: 课程 ID
            file_content: 文件二进制内容
            filename: 原始文件名
            file_type: 文件类型
            created_by: 上传用户 ID

        Returns:
            统一响应格式
        """
        storage_path: Optional[str] = None
        try:
            safe_name = validate_material_upload(
                file_content=file_content,
                filename=filename,
                file_type=file_type,
            )
            # 确定存储路径
            upload_dir = self._get_upload_dir()
            extension = os.path.splitext(safe_name)[1].lower()
            storage_path = os.path.join(upload_dir, f"{uuid4().hex}{extension}")

            # 写入文件
            with open(storage_path, "wb") as f:
                f.write(file_content)

            # 创建数据库记录
            material_id = self._repo.upload_material(
                course_id=course_id,
                filename=safe_name,
                file_type=file_type,
                storage_path=storage_path,
                created_by=created_by,
            )

            return {
                "code": 0,
                "message": "文件上传成功",
                "data": {
                    "material_id": material_id,
                    "filename": safe_name,
                    "file_type": file_type,
                    "status": "pending",
                },
            }

        except ValueError as exc:
            return {"code": 400, "message": str(exc), "data": None}
        except Exception:
            if storage_path and os.path.exists(storage_path):
                try:
                    os.remove(storage_path)
                except OSError:
                    logger.warning("无法清理上传失败的临时文件: %s", storage_path)
            logger.exception("课程资料上传失败")
            return {
                "code": 500,
                "message": "上传失败，请稍后重试",
                "data": None,
            }

    def parse_material(self, material_id: int) -> Dict[str, Any]:
        """
        解析课程资料，生成 chunks，并自动匹配知识点。

        读取文件内容，按类型解析，提取关键词，切分 chunk，存入数据库。
        解析完成后，调用 _match_knowledge_points 将 chunks 与课程知识点关联。

        Args:
            material_id: 资料 ID

        Returns:
            统一响应格式
        """
        try:
            # 获取资料信息
            material = self._repo.get_material(material_id)
            if not material:
                return {"code": 404, "message": "资料不存在", "data": None}

            if material["status"] == "parsed":
                # 已解析过，走重新解析流程
                return self.reparse_material(material_id)

            # 更新状态为 parsing
            self._repo.update_material_status(material_id, "parsing")

            # 首次解析没有可回退版本。
            storage_path = material["storage_path"]
            if not os.path.exists(storage_path):
                self._repo.update_material_status(
                    material_id, "failed", error_message="文件不存在"
                )
                return {"code": 404, "message": "文件不存在", "data": None}

            # 解析文档
            chunks_data = parse_document_file(storage_path, material["file_type"])

            if not chunks_data:
                self._repo.update_material_status(
                    material_id, "failed", error_message="未能提取有效内容"
                )
                return {"code": 400, "message": "未能提取有效内容", "data": None}

            material_version = int(material.get("material_version") or 1)
            final_chunks, total_chars = self._prepare_chunks(chunks_data)
            inserted = self._repo.replace_material_chunks(
                material_id=material_id,
                course_id=material["course_id"],
                chunks=final_chunks,
                material_version=material_version,
                total_chars=total_chars,
            )

            # 知识点预匹配
            match_result = self._match_knowledge_points(material_id, material["course_id"], material_version)

            return {
                "code": 0,
                "message": "解析成功",
                "data": {
                    "material_id": material_id,
                    "total_chunks": inserted,
                    "material_version": material_version,
                    "kp_links_created": match_result,
                    "chunks_preview": [
                        {
                            "title": c["title"],
                            "content_preview": c["content"][:200] + "..."
                            if len(c["content"]) > 200
                            else c["content"],
                        }
                        for c in final_chunks[:3]
                    ],
                },
            }

        except Exception:
            logger.exception("资料解析失败: material_id=%s", material_id)
            self._repo.update_material_status(
                material_id, "failed", error_message="解析失败，请检查文件内容"
            )
            return {"code": 500, "message": "解析失败，请检查文件内容", "data": None}

    def search(
        self,
        course_id: int,
        query: str,
        kp_id: Optional[int] = None,
        limit: int = 5,
    ) -> Dict[str, Any]:
        """
        检索课程知识库 chunks。

        Args:
            course_id: 课程 ID
            query: 查询文本
            kp_id: 可选，限定知识点 ID
            limit: 返回数量

        Returns:
            统一响应格式
        """
        try:
            if not query or not query.strip():
                return {"code": 400, "message": "查询文本不能为空", "data": None}

            chunks = self._repo.search_chunks(
                course_id=course_id,
                query=query,
                kp_id=kp_id,
                limit=limit,
            )

            return {
                "code": 0,
                "message": "检索成功",
                "data": {
                    "query": query,
                    "total": len(chunks),
                    "chunks": chunks,
                },
            }

        except Exception:
            logger.exception("知识库检索失败: course_id=%s", course_id)
            return {"code": 500, "message": "检索失败，请稍后重试", "data": None}

    @staticmethod
    def _prepare_chunks(chunks_data: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], int]:
        final_chunks = []
        for chunk in chunks_data:
            content = chunk["content"]
            final_chunks.append({
                "title": chunk.get("title", ""),
                "content": content,
                "source_page": chunk.get("source_page"),
                "source_paragraph": chunk.get("source_paragraph", 0),
                "bm25_terms": ",".join(extract_bm25_terms(content)),
                "chunk_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            })
        return final_chunks, sum(len(chunk["content"]) for chunk in final_chunks)

    def reparse_material(self, material_id: int) -> Dict[str, Any]:
        """
        重新解析已解析过的资料。

        新内容解析成功后，在单个事务内替换旧 chunks 和关联。

        Args:
            material_id: 资料 ID

        Returns:
            统一响应格式
        """
        try:
            material = self._repo.get_material(material_id)
            if not material:
                return {"code": 404, "message": "资料不存在", "data": None}

            old_version = int(material.get("material_version") or 1)

            # 更新状态为 parsing
            self._repo.update_material_status(material_id, "parsing")

            # 重新解析期间旧片段保持可检索，失败时恢复 parsed 状态。
            storage_path = material["storage_path"]
            if not os.path.exists(storage_path):
                self._repo.update_material_status(
                    material_id, "parsed", error_message="源文件不存在，已保留上一版本"
                )
                return {
                    "code": 404,
                    "message": "源文件不存在，已保留上一版本",
                    "data": None,
                }

            # 重新解析
            chunks_data = parse_document_file(storage_path, material["file_type"])
            if not chunks_data:
                self._repo.update_material_status(
                    material_id, "parsed", error_message="未提取到新内容，已保留上一版本"
                )
                return {
                    "code": 400,
                    "message": "未提取到新内容，已保留上一版本",
                    "data": None,
                }

            # 新版本号 = 旧版本 + 1
            new_version = old_version + 1

            final_chunks, total_chars = self._prepare_chunks(chunks_data)
            inserted = self._repo.replace_material_chunks(
                material_id=material_id,
                course_id=material["course_id"],
                chunks=final_chunks,
                material_version=new_version,
                total_chars=total_chars,
            )

            # 知识点预匹配（使用新版本号）
            match_result = self._match_knowledge_points(material_id, material["course_id"], new_version)

            return {
                "code": 0,
                "message": "重新解析成功",
                "data": {
                    "material_id": material_id,
                    "total_chunks": inserted,
                    "material_version": new_version,
                    "kp_links_created": match_result,
                    "chunks_preview": [
                        {
                            "title": c["title"],
                            "content_preview": c["content"][:200] + "..."
                            if len(c["content"]) > 200
                            else c["content"],
                        }
                        for c in final_chunks[:3]
                    ],
                },
            }

        except Exception:
            logger.exception("资料重新解析失败: material_id=%s", material_id)
            self._repo.update_material_status(
                material_id, "parsed", error_message="重新解析失败，已保留上一版本"
            )
            return {
                "code": 500,
                "message": "重新解析失败，已保留上一版本",
                "data": None,
            }

    def _match_knowledge_points(
        self,
        material_id: int,
        course_id: int,
        material_version: int,
    ) -> int:
        """
        将某资料版本的 chunks 与课程知识点进行 BM25 匹配，写入 kp_chunk_links。

        Args:
            material_id: 资料 ID
            course_id: 课程 ID
            material_version: 资料版本号（用于查询刚插入的 chunks）

        Returns:
            创建的关联数量
        """
        try:
            # 获取课程的所有知识点
            kps = self._evidence_repo.get_kps_by_course(course_id)
            if not kps:
                return 0

            # 查询刚插入的 chunks（按 material_id + material_version）
            chunks = self._repo.get_chunks_by_material_version(material_id, material_version)
            if not chunks:
                return 0

            # 用 BM25 匹配
            links = self._evidence_repo.match_kps_to_chunks(
                chunks=[
                    {
                        "chunk_id": c["chunk_id"],
                        "bm25_terms": c.get("bm25_terms", ""),
                        "content": c.get("content", "")[:200],
                    }
                    for c in chunks
                ],
                kps=kps,
                match_version=material_version,
            )

            if links:
                return self._evidence_repo.upsert_kp_chunk_links(links)

            return 0

        except Exception:
            # 知识点匹配失败不影响主流程
            return 0

    def get_materials(self, course_id: int) -> Dict[str, Any]:
        """
        获取课程资料列表。

        Args:
            course_id: 课程 ID

        Returns:
            统一响应格式
        """
        try:
            materials = self._repo.list_materials(course_id)
            return {
                "code": 0,
                "message": "success",
                "data": {
                    "course_id": course_id,
                    "total": len(materials),
                    "materials": materials,
                },
            }
        except Exception:
            logger.exception("获取课程资料列表失败: course_id=%s", course_id)
            return {"code": 500, "message": "获取资料列表失败，请稍后重试", "data": None}

    def get_material_detail(self, material_id: int) -> Dict[str, Any]:
        """
        获取资料详情（含 chunks）。

        Args:
            material_id: 资料 ID

        Returns:
            统一响应格式
        """
        try:
            material = self._repo.get_material(material_id)
            if not material:
                return {"code": 404, "message": "资料不存在", "data": None}

            chunks = self._repo.get_chunks_by_material(material_id)

            return {
                "code": 0,
                "message": "success",
                "data": {
                    "material": material,
                    "chunks": chunks,
                },
            }
        except Exception:
            logger.exception("获取资料详情失败: material_id=%s", material_id)
            return {"code": 500, "message": "获取资料详情失败，请稍后重试", "data": None}

    def delete_material(self, material_id: int) -> Dict[str, Any]:
        """
        删除课程资料（软删除）。

        Args:
            material_id: 资料 ID

        Returns:
            统一响应格式
        """
        try:
            material = self._repo.get_material(material_id)
            if not material:
                return {"code": 404, "message": "资料不存在", "data": None}

            success = self._repo.delete_material(material_id)
            if success:
                return {"code": 0, "message": "删除成功", "data": {"material_id": material_id}}
            else:
                return {"code": 500, "message": "删除失败", "data": None}

        except Exception:
            logger.exception("删除课程资料失败: material_id=%s", material_id)
            return {"code": 500, "message": "删除失败，请稍后重试", "data": None}
