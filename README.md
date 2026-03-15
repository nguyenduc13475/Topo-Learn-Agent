PROJECT STRUCTURE:

backend/
├── app/
│   ├── api/                    # Chứa các Router/Endpoints của FastAPI
│   │   ├── dependencies.py     # Các hàm inject dependency (VD: get_db, get_current_user)
│   │   ├── v1/
│   │   │   ├── auth.py         # Đăng nhập, đăng ký
│   │   │   ├── document.py     # API upload PDF/Video
│   │   │   ├── graph.py        # API truy vấn Knowledge Graph
│   │   │   ├── quiz.py         # API lấy và nộp bài Quiz
│   │   │   └── review.py       # API tính toán SM-2, lịch ôn tập
│   │   └── router.py           # Gom tất cả router v1 lại
│   ├── core/                   # Cấu hình lõi của ứng dụng
│   │   ├── config.py           # Load biến môi trường từ .env (Pydantic BaseSettings)
│   │   ├── exceptions.py       # Custom exception (ItemNotFound, Unauthorized...)
│   │   └── security.py         # Hash password, mã hóa JWT token
│   ├── db/                     # Kết nối cơ sở dữ liệu
│   │   ├── postgres.py         # Sessionmaker cho PostgreSQL (SQLAlchemy)
│   │   └── neo4j.py            # Driver kết nối cho Neo4j
│   ├── models/                 # SQLAlchemy Models (Định nghĩa bảng trong Postgres)
│   │   ├── user.py
│   │   ├── document.py
│   │   └── sm2_progress.py
│   ├── schemas/                # Pydantic Models (Validate input/output API)
│   │   ├── document_schema.py
│   │   ├── quiz_schema.py
│   │   └── graph_schema.py
│   ├── services/               # Nơi chứa toàn bộ Business Logic (không gọi trực tiếp ở API)
│   │   ├── ingestion_svc.py    # Logic chia nhỏ file, bóc tách text
│   │   ├── graph_svc.py        # Logic tạo Node, tìm Dependency, Topological sort
│   │   ├── sm2_svc.py          # Implement thuật toán SuperMemo-2
│   │   ├── recommendation_svc.py # Implement tính năng gợi ý concept tiếp theo nên học
│   │   └── tutor_svc.py        # Logic chấm điểm, giải thích lỗi sai
│   └── ai_modules/             # Các module AI phục vụ cho Services
│       ├── vision/             
│       │   ├── yolo_layout.py  # Load weights và inference YOLOv8
│       │   └── table_tf.py     # Chạy Table Transformer
│       ├── audio/
│       │   ├── whisper_asr.py  # Chạy Whisper small
│       │   └── scene_split.py  # Chạy PySceneDetect
│       └── llm/
│           ├── gemini_client.py# Wrapper để gọi Gemini 1.5 API (Structured Output)
│           └── prompts.py      # Lưu trữ toàn bộ System Prompts dưới dạng string/template
├── data/                       # Thư mục chứa dữ liệu tĩnh (Sẽ ignore các file lớn)
│   ├── uploads/                # File PDF/Video user upload (trong môi trường dev)
│   └── weights/                # Chứa file .pt của YOLO, model của Whisper
├── tests/                      # Thư mục viết Unit Test (Pytest)
│   ├── conftest.py             # Fixtures cho pytest
│   ├── test_api/               # Test các endpoint
│   └── test_services/          # Test logic
├── scripts/                    # Thư mục script
│   ├── train_yolo.py           # Train YOLO
│   └── download_models.py      # Download YOLO
├── .env.example                # File mẫu chứa tên các biến môi trường
├── .env                        # File thật chứa tên các biến môi trường
├── main.py                     # Entry point khởi chạy FastAPI app
├── pyproject.toml              # Quản lý dependencies (nếu dùng Poetry, hoặc dùng requirements.txt)
└── requirements.txt            # Danh sách thư viện (nếu dùng pip)
frontend/
.gitignore                      # Bỏ qua __pycache__, venv, data/uploads, file .env
docker-compose.yml              # Script để spin-up nhanh PostgreSQL và Neo4j
README.md                       # Giới thiệu kiến trúc, cách cài đặt, cách chạy lệnh
