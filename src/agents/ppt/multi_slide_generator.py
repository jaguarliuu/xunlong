"""
Multi-Slide PPT Generator - 多页HTML PPT生成器

每页独立HTML架构，支持并行生成和灵活导航
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
from jinja2 import Environment, FileSystemLoader, Template


class MultiSlidePPTGenerator:
    """多页HTML PPT生成器"""

    def __init__(self, llm_manager=None, prompt_manager=None, template_dir: Optional[Path] = None):
        """
        初始化PPT生成器

        Args:
            llm_manager: LLM管理器（用于生成页面内容）
            prompt_manager: Prompt管理器
            template_dir: 模板目录路径
        """
        self.llm_manager = llm_manager
        self.prompt_manager = prompt_manager
        self.template_dir = template_dir or self._get_default_template_dir()
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )

        # PPT配置
        self.slide_size = {"width": 1280, "height": 720}
        self.aspect_ratio = "16:9"

        logger.info(f"[MultiSlidePPTGenerator] 初始化完成，模板目录: {self.template_dir}")

    def _get_default_template_dir(self) -> Path:
        """获取默认模板目录"""
        return Path(__file__).parent / 'templates'

    async def generate_ppt(
        self,
        slides_data: List[Dict[str, Any]],
        ppt_config: Dict[str, Any],
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        生成完整的多页PPT

        Args:
            slides_data: 幻灯片数据列表
            ppt_config: PPT配置
            output_dir: 输出目录

        Returns:
            生成结果
        """
        try:
            logger.info(f"[MultiSlidePPTGenerator] 开始生成PPT，共 {len(slides_data)} 页")

            # 1. 创建输出目录结构
            ppt_dir = self._create_directory_structure(output_dir)

            # 2. 生成幻灯片元数据
            metadata = self._create_slides_metadata(slides_data, ppt_config)

            # 3. 并行生成所有幻灯片
            slide_files = await self._generate_all_slides(
                slides_data, metadata, ppt_dir
            )

            # 4. 生成导航页面
            self._generate_navigation_pages(metadata, ppt_dir)

            # 5. 保存元数据
            self._save_metadata(metadata, ppt_dir)

            # 6. 复制公共资源
            self._copy_common_assets(ppt_dir)

            logger.info(f"[MultiSlidePPTGenerator] PPT生成完成: {ppt_dir}")

            return {
                "status": "success",
                "ppt_dir": str(ppt_dir),
                "total_slides": len(slides_data),
                "slide_files": slide_files,
                "index_page": str(ppt_dir / "index.html"),
                "presenter_page": str(ppt_dir / "presenter.html")
            }

        except Exception as e:
            logger.error(f"[MultiSlidePPTGenerator] PPT生成失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _create_directory_structure(self, output_dir: Path) -> Path:
        """创建PPT目录结构"""
        ppt_dir = output_dir / "ppt"
        ppt_dir.mkdir(parents=True, exist_ok=True)

        # 创建子目录
        (ppt_dir / "slides").mkdir(exist_ok=True)
        (ppt_dir / "assets" / "styles").mkdir(parents=True, exist_ok=True)
        (ppt_dir / "assets" / "scripts").mkdir(parents=True, exist_ok=True)
        (ppt_dir / "assets" / "images").mkdir(parents=True, exist_ok=True)
        (ppt_dir / "data").mkdir(exist_ok=True)

        logger.info(f"[MultiSlidePPTGenerator] 目录结构创建完成: {ppt_dir}")
        return ppt_dir

    def _create_slides_metadata(
        self,
        slides_data: List[Dict[str, Any]],
        ppt_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建幻灯片元数据"""
        total_slides = len(slides_data)

        slides_meta = []
        for i, slide_data in enumerate(slides_data):
            slide_number = i + 1
            slide_type = slide_data.get('type', 'content')

            # 生成文件名
            file_name = f"slide_{slide_number:02d}_{slide_type}.html"

            # 确定前后页
            prev_file = f"slide_{slide_number-1:02d}_{slides_data[i-1].get('type', 'content')}.html" if i > 0 else None
            next_file = f"slide_{slide_number+1:02d}_{slides_data[i+1].get('type', 'content')}.html" if i < total_slides - 1 else None

            slides_meta.append({
                "slide_id": f"slide_{slide_number:02d}",
                "slide_number": slide_number,
                "file_name": file_name,
                "type": slide_type,
                "title": slide_data.get('title', f'Slide {slide_number}'),
                "template": slide_data.get('template', slide_type),
                "prev": prev_file,
                "next": next_file
            })

        metadata = {
            "ppt_title": ppt_config.get('title', 'Untitled Presentation'),
            "total_slides": total_slides,
            "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "theme": ppt_config.get('theme', 'business'),
            "color_scheme": ppt_config.get('color_scheme', {
                "primary": "#2E8B57",
                "secondary": "#FF8C00",
                "accent": "#E6E6FA"
            }),
            "slides": slides_meta
        }

        return metadata

    async def _generate_all_slides(
        self,
        slides_data: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        ppt_dir: Path
    ) -> List[str]:
        """并行生成所有幻灯片"""
        tasks = []

        for i, slide_data in enumerate(slides_data):
            slide_meta = metadata['slides'][i]
            task = self._generate_single_slide(
                slide_data, slide_meta, metadata, ppt_dir
            )
            tasks.append(task)

        # 并行执行
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 检查结果
        slide_files = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"[MultiSlidePPTGenerator] 幻灯片 {i+1} 生成失败: {result}")
            else:
                slide_files.append(result)

        logger.info(f"[MultiSlidePPTGenerator] 成功生成 {len(slide_files)}/{len(slides_data)} 页")
        return slide_files

    async def _generate_single_slide(
        self,
        slide_data: Dict[str, Any],
        slide_meta: Dict[str, Any],
        ppt_metadata: Dict[str, Any],
        ppt_dir: Path
    ) -> str:
        """生成单个幻灯片页面"""
        try:
            slide_number = slide_meta['slide_number']
            slide_type = slide_meta['type']

            logger.info(f"[MultiSlidePPTGenerator] 生成幻灯片 {slide_number}: {slide_meta['title']}")

            # 检查是否已经有LLM生成的HTML内容 (V3模式)
            if 'html_content' in slide_data:
                # V3模式：直接使用PageAgent生成的HTML
                html_content = slide_data['html_content']
                logger.info(f"[MultiSlidePPTGenerator] 使用PageAgent生成的HTML (V3模式)")
            else:
                # V2兼容模式：使用Jinja2模板渲染
                # 1. 选择模板
                template_name = self._get_template_name(slide_type)
                template = self.jinja_env.get_template(template_name)

                # 2. 准备渲染数据
                render_data = {
                    # 幻灯片内容
                    "content": slide_data.get('content', {}),

                    # 页面元数据
                    "slide_number": slide_number,
                    "total_slides": ppt_metadata['total_slides'],
                    "slide_title": slide_meta['title'],
                    "slide_type": slide_type,

                    # 导航信息
                    "prev_slide": slide_meta['prev'],
                    "next_slide": slide_meta['next'],

                    # 主题配置
                    "theme": ppt_metadata['theme'],
                    "colors": ppt_metadata['color_scheme'],

                    # PPT信息
                    "ppt_title": ppt_metadata['ppt_title'],

                    # AIGC元数据
                    "aigc_metadata": self._generate_aigc_metadata()
                }

                # 3. 渲染HTML
                html_content = template.render(**render_data)
                logger.info(f"[MultiSlidePPTGenerator] 使用Jinja2模板渲染HTML (V2兼容模式)")

            # 4. 包装HTML为完整页面（添加导航和基础结构）
            html_content = self._wrap_slide_html(
                html_content,
                slide_meta,
                ppt_metadata
            )

            # 5. 保存文件
            output_file = ppt_dir / "slides" / slide_meta['file_name']
            output_file.write_text(html_content, encoding='utf-8')

            logger.info(f"[MultiSlidePPTGenerator] 幻灯片 {slide_number} 已保存: {output_file.name}")
            return str(output_file)

        except Exception as e:
            logger.error(f"[MultiSlidePPTGenerator] 幻灯片 {slide_number} 生成失败: {e}")
            raise

    def _wrap_slide_html(
        self,
        content_html: str,
        slide_meta: Dict[str, Any],
        ppt_metadata: Dict[str, Any]
    ) -> str:
        """
        处理幻灯片HTML

        V3架构：不再注入导航组件，保持LLM生成的HTML纯净
        导航由presenter.html容器页面统一处理
        """
        slide_number = slide_meta['slide_number']

        # 检查是否已经是完整的HTML文档
        is_complete_html = '<!DOCTYPE' in content_html or '<html' in content_html

        if is_complete_html:
            # LLM生成的是完整HTML，直接返回，不做任何修改
            logger.info(f"[MultiSlidePPTGenerator] Slide {slide_number}: 使用LLM生成的完整HTML，保持纯净")
            return content_html
        else:
            # 不是完整HTML，需要完整包装
            return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{slide_meta['title']} - {ppt_metadata['ppt_title']}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet"/>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body, html {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, "Seguro UI", sans-serif;
        }}
        .slide-controls {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            z-index: 1000;
        }}
        .nav-btn {{
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid #ddd;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .nav-btn:hover {{
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .nav-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        .slide-number {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            z-index: 1000;
        }}
    </style>
</head>
<body>
    {content_html}

    <div class="slide-number">
        {slide_number} / {total_slides}
    </div>

    <div class="slide-controls">
        <button class="nav-btn" onclick="window.location.href='../index.html'">
            <i class="fas fa-home"></i> 首页
        </button>
        {'<button class="nav-btn" onclick="window.location.href=\'' + prev_slide + '\'"><i class="fas fa-arrow-left"></i> 上一页</button>' if prev_slide else '<button class="nav-btn" disabled><i class="fas fa-arrow-left"></i> 上一页</button>'}
        {'<button class="nav-btn" onclick="window.location.href=\'' + next_slide + '\'">下一页 <i class="fas fa-arrow-right"></i></button>' if next_slide else '<button class="nav-btn" disabled>下一页 <i class="fas fa-arrow-right"></i></button>'}
    </div>

    <script>
        // 键盘导航
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowLeft' && '{prev_slide or ''}') {{
                window.location.href = '{prev_slide or ''}';
            }} else if (e.key === 'ArrowRight' && '{next_slide or ''}') {{
                window.location.href = '{next_slide or ''}';
            }} else if (e.key === 'Home') {{
                window.location.href = '../index.html';
            }}
        }});
    </script>
</body>
</html>
"""

    def _get_template_name(self, slide_type: str) -> str:
        """获取模板文件名"""
        template_map = {
            'cover': 'slide_cover.html',
            'toc': 'slide_toc.html',
            'content': 'slide_content.html',
            'chart': 'slide_chart.html',
            'comparison': 'slide_comparison.html',
            'summary': 'slide_summary.html'
        }
        return template_map.get(slide_type, 'slide_content.html')

    def _generate_navigation_pages(
        self,
        metadata: Dict[str, Any],
        ppt_dir: Path
    ):
        """生成导航页面"""
        # 1. 生成index.html (缩略图导航)
        self._generate_index_page(metadata, ppt_dir)

        # 2. 生成presenter.html (演示模式)
        self._generate_presenter_page(metadata, ppt_dir)

    def _generate_index_page(self, metadata: Dict[str, Any], ppt_dir: Path):
        """生成导航入口页"""
        try:
            template = self.jinja_env.get_template('index.html')
            html = template.render(metadata=metadata)

            output_file = ppt_dir / "index.html"
            output_file.write_text(html, encoding='utf-8')

            logger.info(f"[MultiSlidePPTGenerator] 导航页面已生成: index.html")
        except Exception as e:
            logger.warning(f"[MultiSlidePPTGenerator] 导航页面生成失败: {e}")

    def _generate_presenter_page(self, metadata: Dict[str, Any], ppt_dir: Path):
        """生成演示模式页面"""
        try:
            template = self.jinja_env.get_template('presenter.html')
            html = template.render(metadata=metadata)

            output_file = ppt_dir / "presenter.html"
            output_file.write_text(html, encoding='utf-8')

            logger.info(f"[MultiSlidePPTGenerator] 演示页面已生成: presenter.html")
        except Exception as e:
            logger.warning(f"[MultiSlidePPTGenerator] 演示页面生成失败: {e}")

    def _save_metadata(self, metadata: Dict[str, Any], ppt_dir: Path):
        """保存元数据到JSON文件"""
        metadata_file = ppt_dir / "data" / "slides_metadata.json"
        metadata_file.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        logger.info(f"[MultiSlidePPTGenerator] 元数据已保存: {metadata_file}")

    def _copy_common_assets(self, ppt_dir: Path):
        """复制公共资源文件"""
        # TODO: 复制通用CSS、JS等资源
        # 目前使用CDN，暂不需要本地资源
        logger.info("[MultiSlidePPTGenerator] 公共资源处理完成")

    def _generate_aigc_metadata(self) -> str:
        """生成AIGC元数据"""
        import uuid
        project_id = str(uuid.uuid4())[:32]

        metadata = {
            "AIGC": {
                "Label": "1",
                "ContentProducer": "xunlong",
                "ProduceID": project_id,
                "ContentPropagator": "xunlong",
                "PropagateID": project_id
            }
        }
        return json.dumps(metadata, ensure_ascii=False)


# 辅助函数

def create_slide_data(
    slide_type: str,
    title: str,
    content: Dict[str, Any],
    template: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建幻灯片数据结构

    Args:
        slide_type: 幻灯片类型 (cover, toc, content, chart, etc.)
        title: 幻灯片标题
        content: 幻灯片内容
        template: 可选的自定义模板名

    Returns:
        幻灯片数据字典
    """
    return {
        "type": slide_type,
        "title": title,
        "content": content,
        "template": template or slide_type
    }
