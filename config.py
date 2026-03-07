# =========================
# Storage configuration
# =========================

BASE_DOWNLOAD_DIR = "downloads"

DATABASE_NAME = "qdarchive.db"


# =========================
# Networking configuration
# =========================

MAX_THREADS = 6

REQUEST_TIMEOUT = 30


# =========================
# Search queries
# =========================

SEARCH_QUERIES = [

"qualitative interview",
"qualitative research",
"ethnography",
"focus group",
"field study",
"interview transcript",
"social research",
"qualitative dataset",
"case study",
"participant observation",
"grounded theory",
"research interviews",
"qualitative fieldwork",
"qualitative coding",
"narrative interview",
"life history interview",
"oral history",
"focus group discussion",
"social science interview",
"human subject interview",
"anthropology field notes",
"qualitative sociology",
"interview data",
"qualitative study"
]


# =========================
# QDA Software File Types
# =========================

QDA_EXTENSIONS = [

".qdpx",
".nvpx",
".nvp",
".atlproj",
".atlasti",
".mx12",
".mx24",
".qdc",
".mqda"
]


# =========================
# Primary Research Data
# =========================

PRIMARY_EXTENSIONS = [

".pdf",
".doc",
".docx",
".txt",
".rtf",
".xlsx",
".xls",
".csv",
".zip",
".tar",
".gz",
".mp3",
".wav",
".mp4"
]


# =========================
# Combined extensions
# =========================

ALLOWED_EXTENSIONS = QDA_EXTENSIONS + PRIMARY_EXTENSIONS