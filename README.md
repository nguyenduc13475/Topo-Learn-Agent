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

frontend/src/
├── app/                          # Next.js App Router (Chỉ chứa Routing và Page/Layout)
│   ├── (auth)/                   # Route group cho đăng nhập/đăng ký (không có sidebar)
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (dashboard)/              # Route group cho app chính (có Sidebar & Header)
│   │   ├── layout.tsx            # Chứa Sidebar (Tiến trình học) và Topbar
│   │   ├── page.tsx              # Trang chủ Dashboard (Tổng quan tiến trình SM-2)
│   │   ├── documents/            # Quản lý tài liệu (Upload, List)
│   │   │   └── page.tsx
│   │   ├── graph/[docId]/        # Vẽ Knowledge Graph cho từng Document
│   │   │   └── page.tsx
│   │   ├── learn/[conceptId]/    # Trang học Concept (Định nghĩa, Video, AI Chat)
│   │   │   └── page.tsx
│   │   └── quiz/[conceptId]/     # Trang làm bài Quiz sinh bởi Gemini
│   │       └── page.tsx
│   ├── globals.css               # Đã có
│   └── layout.tsx                # Root layout (Provider, Font, Toast)
│
├── features/                     # CHÌA KHÓA SCALING: Chia component & logic theo nghiệp vụ
│   ├── auth/                     # Tính năng xác thực
│   │   ├── components/           # VD: LoginForm, RegisterForm
│   │   └── api/                  # VD: login() gọi API backend
│   ├── document-upload/          # Tính năng xử lý tài liệu
│   │   ├── components/           # VD: Dropzone, UploadProgress, DocumentCard
│   │   └── api/                  # VD: uploadFile(), getDocuments()
│   ├── knowledge-graph/          # Tính năng đồ thị tri thức
│   │   ├── components/           # VD: FlowCanvas (dùng React Flow vẽ Node/Edge)
│   │   └── hooks/                # VD: useGraphData()
│   ├── learning/                 # Tính năng hiển thị bài học và Chat với Tutor
│   │   ├── components/           # VD: ConceptViewer, TutorChatBox, MarkdownRenderer
│   │   └── api/                  # VD: getConceptContext()
│   └── quiz-review/              # Tính năng trắc nghiệm và SM-2
│       ├── components/           # VD: MultipleChoiceOption, QuizResult, ForgettingCurveChart
│       └── hooks/                # VD: useCalculateSM2()
│
├── components/                   # Chứa các component UI dùng chung (Dumb Components)
│   ├── ui/                       # Nơi chứa TẤT CẢ components của Shadcn UI (Button, Card, Dialog...)
│   ├── layout/                   # UI cấu trúc trang (Sidebar, Navbar, UserDropdown)
│   └── shared/                   # Các UI nhỏ tự viết dùng nhiều nơi (LoadingSpinner, EmptyState)
│
├── lib/                          # Các hàm tiện ích, cấu hình
│   ├── api-client.ts             # Cấu hình Axios/Fetch instance (đính kèm JWT Token)
│   ├── utils.ts                  # Đã có (cn tailwind)
│   └── sm2-helpers.ts            # (Tùy chọn) Logic tính ngày ôn tập ở Frontend nếu cần hiển thị
│
├── hooks/                        # Custom Hooks dùng chung toàn app
│   ├── use-debounce.ts
│   └── use-auth.ts               # Hook quản lý JWT token và phiên đăng nhập
│
├── store/                        # Global State (Zustand hoặc Redux)
│   ├── useUIStore.ts             # Quản lý trạng thái đóng/mở Sidebar, Theme
│   └── useLearnStore.ts          # Quản lý tiến trình học hiện tại (Concept đang học)
│
└── types/                        # Định nghĩa TypeScript Interfaces đồng bộ với Schema của FastAPI
    ├── document.d.ts
    ├── graph.d.ts
    └── quiz.d.ts

.gitignore                      # Bỏ qua __pycache__, venv, data/uploads, file .env
docker-compose.yml              # Script để spin-up nhanh PostgreSQL và Neo4j
README.md                       # Giới thiệu kiến trúc, cách cài đặt, cách chạy lệnh


Tại sao lại chọn cấu trúc này (frontend)?
Giảm tải cho app/: Thư mục app/ rất dễ bị lộn xộn nếu bạn nhét cả Component và Logic vào đó. Với cấu trúc này, các file page.tsx sẽ rất sạch, chỉ làm nhiệm vụ lấy params từ URL và gọi component từ thư mục features/ ra để render.

Sức mạnh của thư mục features/: Khi bạn cần sửa luồng làm bài Quiz, bạn chỉ cần vào src/features/quiz-review/. Tất cả API calls, Hooks, và UI components của Quiz đều nằm gom lại một chỗ. Điều này giúp hệ thống không bị "rối rắm" khi dự án lớn lên.

Phân tách Rõ ràng (Separation of Concerns): components/ui/ chỉ chứa các nút bấm, thẻ bài (Shadcn). Nó không biết API là gì. Việc gọi API là việc của features/.