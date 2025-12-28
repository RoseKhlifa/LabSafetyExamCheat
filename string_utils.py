# string_utils.py
import re
from typing import List, Dict


class StringUtils:
    """字符串处理工具类"""

    @staticmethod
    def split(text: str, sep: str) -> List[str]:
        """按指定字符或字符串分割"""
        if text is None:
            return []
        return text.split(sep)

    @staticmethod
    def split_multi(text: str, seps: List[str]) -> List[str]:
        """按多个分隔符分割"""
        if not text:
            return []
        pattern = "|".join(map(re.escape, seps))
        return [s for s in re.split(pattern, text) if s]

    @staticmethod
    def split_lines(text: str) -> List[str]:
        """按行拆分，自动处理 \\r\\n"""
        if not text:
            return []
        return text.replace('\r', '').split('\n')

    @staticmethod
    def remove_empty_lines(text: str) -> str:
        """删除空行"""
        lines = StringUtils.split_lines(text)
        return '\n'.join(line for line in lines if line.strip())

    @staticmethod
    def trim(text: str) -> str:
        """去除首尾空白"""
        return text.strip() if text else ""

    @staticmethod
    def normalize_space(text: str) -> str:
        """合并多个空白为一个空格"""
        return re.sub(r'\s+', ' ', text).strip() if text else ""

    @staticmethod
    def remove_chars(text: str, chars: str) -> str:
        """移除指定字符"""
        if not text:
            return ""
        return text.translate(str.maketrans('', '', chars))

    @staticmethod
    def clean_text(text: str) -> str:
        """
        常用清洗：
        - 去 \\r
        - 去空行
        - 每行 trim
        """
        if not text:
            return ""
        lines = (
            line.strip()
            for line in text.replace('\r', '').split('\n')
            if line.strip()
        )
        return '\n'.join(lines)

    @staticmethod
    def is_empty(text: str) -> bool:
        """判断是否为空字符串"""
        return not text or not text.strip()

    @staticmethod
    def contains_any(text: str, keywords: List[str]) -> bool:
        """是否包含任意关键词"""
        if not text:
            return False
        return any(k in text for k in keywords)

    @staticmethod
    def is_numeric(text: str) -> bool:
        """是否全为数字"""
        return text.isdigit() if text else False

    @staticmethod
    def truncate(text: str, length: int, suffix: str = "...") -> str:
        """安全截断字符串"""
        if not text or len(text) <= length:
            return text
        return text[:length] + suffix

    @staticmethod
    def char_frequency(text: str) -> Dict[str, int]:
        """统计字符频率"""
        freq = {}
        for ch in text or "":
            freq[ch] = freq.get(ch, 0) + 1
        return freq
    @staticmethod
    def get_sub_str(text: str, start: str, end: str) -> str:
        """
        从 text 中提取 start 和 end 之间的子字符串（不包含 start / end）

        示例:
            get_sub_str("abc[123]def", "[", "]") -> "123"

        规则:
        - start 或 end 不存在时返回 ""
        - end 必须出现在 start 之后
        """

        if not text or not start or not end:
            return ""

        start_index = text.find(start)
        if start_index == -1:
            return ""

        start_index += len(start)

        end_index = text.find(end, start_index)
        if end_index == -1:
            return ""

        return text[start_index:end_index]

