"""学生画像 Repository"""


class ProfileRepository:
    """学生画像数据访问层（当前使用 Mock 数据）"""

    def list_profiles(self, page: int = 1, page_size: int = 20, course_id=None, keyword=None):
        pass

    def get_profile(self, profile_id: int):
        pass

    def update_profile(self, profile_id: int, data: dict):
        pass
