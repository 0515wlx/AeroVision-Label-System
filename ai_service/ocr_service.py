"""
OCR服务模块
支持本地 PaddleOCR 和远程 OCR API 识别注册号
"""

import os
import logging
import re
import json
import base64
import requests
from typing import Dict, Any, Optional
from PIL import Image
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 注册号正则表达式
REGISTRATION_PATTERN = re.compile(
    r"\b([A-Z]{1,2})[- ]?([A-HJ-NP-Z0-9][A-HJ-NP-Z0-9]{0,4})\b"
)


class RegistrationOCR:
    """注册号OCR识别器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化OCR识别器

        Args:
            config: OCR配置
        """
        self.enabled = config.get("enabled", True)
        self.timeout = config.get("timeout", 30)
        self.use_local_paddle = False

        # 检查是否配置了 OCR API URL
        self.api_url = os.getenv("OCR_API_URL")
        if self.api_url:
            logger.info(f"Using remote OCR API: {self.api_url}")
        else:
            # 回退到本地 PaddleOCR
            logger.info("OCR_API_URL not configured, using local PaddleOCR")
            self.use_local_paddle = True
            self._init_local_paddleocr(config)

        logger.info("OCR initialized")

    def _init_local_paddleocr(self, config: Dict[str, Any]):
        """初始化本地 PaddleOCR"""
        try:
            from paddleocr import PaddleOCR

            # 构建初始化参数（移除不支持的参数）
            ocr_init_params = {"use_angle_cls": True, "lang": "en"}

            try:
                import paddle

                if paddle.is_compiled_with_cuda():
                    ocr_init_params["use_gpu"] = True
            except Exception:
                logger.warning("Failed to check CUDA availability, using CPU")

            # 尝试初始化 PaddleOCR
            try:
                self.ocr = PaddleOCR(**ocr_init_params)
                logger.info(f"PaddleOCR initialized successfully (lang=en, gpu=True)")
            except TypeError as e:
                # 如果参数错误，使用基本参数
                if "use_gpu" in str(e) or "show_log" in str(e):
                    ocr_init_params = {"use_angle_cls": True, "lang": "en"}
                    self.ocr = PaddleOCR(**ocr_init_params)
                    logger.info("PaddleOCR initialized with basic params")
                else:
                    raise

        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            self.ocr = None
            self.enabled = False

    def recognize(self, image_path: str) -> Dict[str, Any]:
        """
        识别注册号

        Args:
            image_path: 图片文件路径

        Returns:
            包含识别结果的字典
        """
        if not self.enabled:
            return {
                "registration": "",
                "confidence": 0.0,
                "raw_text": "",
                "all_matches": [],
                "yolo_boxes": [],
            }

        if self.use_local_paddle and self.ocr:
            return self._recognize_local(image_path)
        else:
            return self._recognize_remote(image_path)

    def _recognize_remote(self, image_path: str) -> Dict[str, Any]:
        """使用远程 OCR API 识别"""
        try:
            # 读取图片并转换为 base64
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            # 调用远程 API
            response = requests.post(
                self.api_url,
                json={"image_base64": image_data},
                timeout=self.timeout,
            )

            response.raise_for_status()
            result = response.json()

            # 解析返回结果
            if result.get("error"):
                logger.error(f"OCR API error: {result['error']}")
                return self._empty_result()

            return {
                "registration": result.get("registration", ""),
                "confidence": result.get("confidence", 0.0),
                "raw_text": result.get("raw_text", ""),
                "all_matches": result.get("all_matches", []),
                "yolo_boxes": result.get("yolo_boxes", []),
                "registration_area": result.get("registration_area", ""),
            }

        except Exception as e:
            logger.error(f"OCR API request failed: {e}")
            return self._empty_result()

    def _recognize_local(self, image_path: str) -> Dict[str, Any]:
        """使用本地 PaddleOCR 识别"""
        try:
            # 加载图片
            image = Image.open(image_path)
            img_array = np.array(image)
            img_width, img_height = image.size

            # OCR识别（注意：PaddleOCR 3.x 不支持 cls 参数）
            ocr_results = self.ocr.ocr(img_array)

            if not ocr_results or not ocr_results[0]:
                return self._empty_result()

            all_texts = []
            yolo_boxes = []

            # 处理每个识别结果
            for result in ocr_results[0]:
                if not result or len(result) < 2:
                    continue

                box_points = result[0]
                text_info = result[1]

                if not box_points or not text_info:
                    continue

                text = text_info[0]
                confidence = text_info[1]

                # 提取边界框
                xmin = min(point[0] for point in box_points)
                ymin = min(point[1] for point in box_points)
                xmax = max(point[0] for point in box_points)
                ymax = max(point[1] for point in box_points)

                # 转换为YOLO格式
                x_center = (xmin + xmax) / 2.0 / img_width
                y_center = (ymin + ymax) / 2.0 / img_height
                box_width = (xmax - xmin) / img_width
                box_height = (ymax - ymin) / img_height

                all_texts.append(
                    {
                        "text": text,
                        "confidence": confidence,
                        "box": [x_center, y_center, box_width, box_height],
                    }
                )

                yolo_boxes.append(
                    {
                        "class_id": 0,
                        "x_center": round(x_center, 6),
                        "y_center": round(y_center, 6),
                        "width": round(box_width, 6),
                        "height": round(box_height, 6),
                        "text": text,
                        "confidence": float(confidence),
                    }
                )

            raw_text = " ".join([t["text"] for t in all_texts])
            matches = self._filter_registrations(all_texts)

            if not matches:
                return {
                    "registration": "",
                    "confidence": 0.0,
                    "raw_text": raw_text,
                    "all_matches": [],
                    "yolo_boxes": yolo_boxes,
                    "registration_area": "",
                }

            best_match = max(matches, key=lambda x: x["confidence"])
            yolo_box = best_match.get("box")

            registration_area = ""
            if yolo_box:
                registration_area = (
                    f"{yolo_box[0]} {yolo_box[1]} {yolo_box[2]} {yolo_box[3]}"
                )

            return {
                "registration": best_match["text"],
                "confidence": float(best_match["confidence"]),
                "raw_text": raw_text,
                "all_matches": matches,
                "yolo_boxes": yolo_boxes,
                "registration_area": registration_area,
            }

        except Exception as e:
            logger.error(f"OCR recognition error: {e}")
            return self._empty_result()

    def _empty_result(self) -> Dict[str, Any]:
        """返回空结果"""
        return {
            "registration": "",
            "confidence": 0.0,
            "raw_text": "",
            "all_matches": [],
            "yolo_boxes": [],
            "registration_area": "",
        }

    def _filter_registrations(self, ocr_results: list) -> list:
        """使用正则表达式过滤注册号"""
        matches = []

        for result in ocr_results:
            text = result["text"]
            confidence = result["confidence"]

            match = REGISTRATION_PATTERN.search(text)
            if match:
                registration = match.group(0)
                matches.append(
                    {
                        "text": registration,
                        "confidence": confidence,
                        "box": result["box"],
                    }
                )

        return matches

    def cleanup(self):
        """清理OCR资源，释放内存"""
        if self.use_local_paddle and self.ocr is not None:
            del self.ocr
            self.ocr = None
            logger.info("PaddleOCR resources cleaned up")

        # 清理 CUDA 缓存（如果使用了 GPU）
        try:
            import paddle

            if paddle.is_compiled_with_cuda():
                paddle.device.cuda.empty_cache()
                logger.info("Paddle CUDA cache cleared")
        except Exception:
            pass

    def __del__(self):
        """析构时自动清理"""
        self.cleanup()
