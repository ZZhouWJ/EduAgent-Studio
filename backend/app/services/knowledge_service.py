"""
课程知识库 Service 层。

处理文件上传、文档解析、chunk 生成的业务逻辑。
"""

import os
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.repositories.knowledge_repo import KnowledgeRepository
from app.rag.parser import parse_document, extract_bm25_terms


class KnowledgeService:
    """课程知识库服务层。"""

    def __init__(self) -> None:
        self._repo = KnowledgeRepository()
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
        try:
            # 确定存储路径
            upload_dir = self._get_upload_dir()
            import time
            safe_filename = f"{int(time.time() * 1000)}_{filename}"
            storage_path = os.path.join(upload_dir, safe_filename)

            # 写入文件
            with open(storage_path, "wb") as f:
                f.write(file_content)

            # 创建数据库记录
            material_id = self._repo.upload_material(
                course_id=course_id,
                filename=filename,
                file_type=file_type,
                storage_path=storage_path,
                created_by=created_by,
            )

            return {
                "code": 0,
                "message": "文件上传成功",
                "data": {
                    "material_id": material_id,
                    "filename": filename,
                    "file_type": file_type,
                    "status": "pending",
                },
            }

        except Exception as e:
            return {
                "code": 500,
                "message": f"上传失败: {str(e)}",
                "data": None,
            }

    def parse_material(self, material_id: int) -> Dict[str, Any]:
        """
        解析课程资料，生成 chunks。

        读取文件内容，按类型解析，提取关键词，切分 chunk，存入数据库。

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
                return {"code": 400, "message": "资料已解析过", "data": None}

            # 更新状态为 parsing
            self._repo.update_material_status(material_id, "parsing")

            # 读取文件内容
            storage_path = material["storage_path"]
            if not os.path.exists(storage_path):
                self._repo.update_material_status(
                    material_id, "failed", error_message="文件不存在"
                )
                return {"code": 404, "message": "文件不存在", "data": None}

            with open(storage_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if not content.strip():
                self._repo.update_material_status(
                    material_id, "failed", error_message="文件内容为空"
                )
                return {"code": 400, "message": "文件内容为空", "data": None}

            # 解析文档
            chunks_data = parse_document(content, material["file_type"])

            if not chunks_data:
                self._repo.update_material_status(
                    material_id, "failed", error_message="未能提取有效内容"
                )
                return {"code": 400, "message": "未能提取有效内容", "data": None}

            # 为每个 chunk 提取 BM25 关键词并整理
            final_chunks = []
            for chunk in chunks_data:
                bm25_terms = extract_bm25_terms(chunk["content"])
                final_chunks.append({
                    "title": chunk.get("title", ""),
                    "content": chunk["content"],
                    "source_page": chunk.get("source_page"),
                    "source_paragraph": chunk.get("source_paragraph", 0),
                    "bm25_terms": ",".join(bm25_terms),
                })

            # 批量插入 chunks
            inserted = self._repo.insert_chunks(
                material_id=material_id,
                course_id=material["course_id"],
                chunks=final_chunks,
            )

            # 更新状态为 parsed
            self._repo.update_material_status(
                material_id, "parsed", total_chunks=inserted
            )

            return {
                "code": 0,
                "message": "解析成功",
                "data": {
                    "material_id": material_id,
                    "total_chunks": inserted,
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

        except Exception as e:
            self._repo.update_material_status(
                material_id, "failed", error_message=str(e)
            )
            return {"code": 500, "message": f"解析失败: {str(e)}", "data": None}

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

        except Exception as e:
            return {"code": 500, "message": f"检索失败: {str(e)}", "data": None}

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
        except Exception as e:
            return {"code": 500, "message": f"获取资料列表失败: {str(e)}", "data": None}

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
        except Exception as e:
            return {"code": 500, "message": f"获取资料详情失败: {str(e)}", "data": None}

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

        except Exception as e:
            return {"code": 500, "message": f"删除失败: {str(e)}", "data": None}
