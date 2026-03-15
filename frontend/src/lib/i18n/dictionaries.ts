export const dictionaries = {
  en: {
    sidebar: {
      dashboard: "Dashboard",
      documents: "Documents",
      knowledgeGraph: "Knowledge Graph",
      learning: "Learning Progress",
    },
    topbar: {
      searchPlaceholder: "Search concepts...",
      language: "Language",
      profile: "Profile",
      logout: "Log out",
    },
    common: {
      loading: "Loading...",
      error: "An error occurred.",
    },
  },
  vi: {
    sidebar: {
      dashboard: "Trang chủ",
      documents: "Tài liệu học",
      knowledgeGraph: "Đồ thị tri thức",
      learning: "Tiến trình học",
    },
    topbar: {
      searchPlaceholder: "Tìm kiếm khái niệm...",
      language: "Ngôn ngữ",
      profile: "Hồ sơ",
      logout: "Đăng xuất",
    },
    common: {
      loading: "Đang tải...",
      error: "Đã xảy ra lỗi.",
    },
  },
};

export type Dictionary = typeof dictionaries.en;
