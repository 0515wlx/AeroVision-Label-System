"""
OCR服务模块
使用本地 OCR API 识别注册号
"""

import os
import logging
import re
import json
import base64
import requests
from typing import Dict, Any, Optional
from PIL import Image

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
        # 从环境变量读取 OCR API URL（优先级：环境变量 > 默认值）
        self.api_url = os.getenv('OCR_API_URL', 'http://localhost:8000/v2/models/ocr/infer')
        self.enabled = config.get('enabled', True)
        self.timeout = config.get('timeout', 30)

        if not self.enabled:
            logger.info("OCR is disabled")
            return

        logger.info(f"OCR API initialized (url={self.api_url})")

    def _call_ocr_api(self, image_path: str) -> Optional[Dict]:
        """
        调用 OCR API

        Args:
            image_path: 图片文件路径

        Returns:
            API 响应数据
        """
        try:
            # 读取图片并转换为 base64 编码
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # 构建请求数据，使用 base64 编码的图片
            payload = {
                "inputs": [
                    {
                        "name": "input",
                        "shape": [1, 1],
                        "datatype": "BYTES",
                        "data": [
                            json.dumps({
                                "file": f"data:image/jpeg;base64,{image_base64}",
                                "visualize": False
                            })
                        ]
                    }
                ],
                "outputs": [
                    {
                        "name": "output"
                    }
                ]
            }

            # 发送请求
            response = requests.post(
                self.api_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            response.raise_for_status()

            # 解析响应
            result = response.json()
            if not result.get('outputs'):
                logger.error("No outputs in API response")
                return None

            # 提取并解析 data 字段
            data_str = result['outputs'][0]['data'][0]
            ocr_data = json.loads(data_str)

            return ocr_data

        except FileNotFoundError as e:
            logger.error(f"Image file not found: {image_path}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"OCR API request failed: {e}")
            return None
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Failed to parse OCR API response: {e}")
            return None

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
                "yolo_boxes": []
            }

        try:
            # 获取图片尺寸
            image = Image.open(image_path)
            img_width, img_height = image.size

            # 调用 OCR API
            ocr_data = self._call_ocr_api(image_path)
            if not ocr_data:
                return {
                    "registration": "",
                    "confidence": 0.0,
                    "raw_text": "",
                    "all_matches": [],
                    "yolo_boxes": []
                }

            # 解析 OCR 结果
            try:
                pruned_result = ocr_data['result']['ocrResults'][0]['prunedResult']
                rec_texts = pruned_result.get('rec_texts', [])
                rec_scores = pruned_result.get('rec_scores', [])
                rec_boxes = pruned_result.get('rec_boxes', [])

                if not rec_texts:
                    return {
                        "registration": "",
                        "confidence": 0.0,
                        "raw_text": "",
                        "all_matches": [],
                        "yolo_boxes": []
                    }

            except (KeyError, IndexError) as e:
                logger.error(f"Failed to parse OCR results: {e}")
                return {
                    "registration": "",
                    "confidence": 0.0,
                    "raw_text": "",
                    "all_matches": [],
                    "yolo_boxes": []
                }

            all_texts = []
            yolo_boxes = []

            # 处理每个识别结果
            for i, (text, score, box) in enumerate(zip(rec_texts, rec_scores, rec_boxes)):
                # box 格式: [xmin, ymin, xmax, ymax]
                xmin, ymin, xmax, ymax = box

                # 转换为YOLO格式
                x_center = (xmin + xmax) / 2.0 / img_width
                y_center = (ymin + ymax) / 2.0 / img_height
                box_width = (xmax - xmin) / img_width
                box_height = (ymax - ymin) / img_height

                all_texts.append({
                    "text": text,
                    "confidence": score,
                    "box": [x_center, y_center, box_width, box_height]
                })

                yolo_boxes.append({
                    "class_id": 0,
                    "x_center": round(x_center, 6),
                    "y_center": round(y_center, 6),
                    "width": round(box_width, 6),
                    "height": round(box_height, 6),
                    "text": text,
                    "confidence": float(score)
                })

            raw_text = " ".join(rec_texts)
            matches = self._filter_registrations(all_texts)

            if not matches:
                return {
                    "registration": "",
                    "confidence": 0.0,
                    "raw_text": raw_text,
                    "all_matches": [],
                    "yolo_boxes": yolo_boxes
                }

            best_match = max(matches, key=lambda x: x["confidence"])

            return {
                "registration": best_match["text"],
                "confidence": float(best_match["confidence"]),
                "raw_text": raw_text,
                "all_matches": matches,
                "yolo_boxes": yolo_boxes
            }

        except Exception as e:
            logger.error(f"OCR recognition error: {e}")
            return {
                "registration": "",
                "confidence": 0.0,
                "raw_text": "",
                "all_matches": [],
                "yolo_boxes": []
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
                matches.append({
                    "text": registration,
                    "confidence": confidence,
                    "box": result["box"]
                })

        return matches

    def cleanup(self):
        """清理OCR资源，释放内存"""
        logger.info("OCR API client cleanup (no resources to release)")

    def __del__(self):
        """析构时自动清理"""
        pass
