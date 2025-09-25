# DeepSearch Makefile

.PHONY: help install install-dev test run-cli run-api clean lint format

help:  ## 显示帮助信息
	@echo "DeepSearch 开发工具"
	@echo ""
	@echo "可用命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## 安装依赖
	pip install -r requirements.txt
	python -m playwright install chromium

install-dev:  ## 安装开发依赖
	pip install -r requirements.txt
	pip install black isort flake8 pytest
	python -m playwright install chromium

test:  ## 运行测试
	python test_deepsearch.py

test-examples:  ## 运行示例
	python examples/basic_usage.py

run-cli:  ## 运行CLI示例
	python main.py search "Python教程" --topk 3 --verbose

run-api:  ## 启动API服务
	python run_api.py

test-api:  ## 测试API
	python examples/api_client.py

clean:  ## 清理临时文件
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf build/ dist/ *.egg-info/
	rm -rf shots/ test_shots/ example_shots/ custom_shots/
	rm -f *.json test_*.json

lint:  ## 代码检查
	flake8 src/ --max-line-length=100 --ignore=E203,W503
	isort --check-only src/

format:  ## 格式化代码
	black src/ --line-length=100
	isort src/

build:  ## 构建包
	python setup.py sdist bdist_wheel

install-package:  ## 安装本地包
	pip install -e .

docker-build:  ## 构建Docker镜像
	docker build -t deepsearch:latest .

docker-run:  ## 运行Docker容器
	docker run -p 8000:8000 deepsearch:latest