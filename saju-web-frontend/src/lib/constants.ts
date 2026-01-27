
export const ELEMENT_COLORS: Record<string, string> = {
    // Wood (Mok) - Green/Blue
    "목": "text-green-400",
    "갑": "text-green-400",
    "을": "text-green-400",
    "인": "text-green-400",
    "묘": "text-green-400",

    // Fire (Hwa) - Red
    "화": "text-red-400",
    "병": "text-red-400",
    "정": "text-red-400",
    "사": "text-red-400",
    "오": "text-red-400",

    // Earth (To) - Yellow/Brown
    "토": "text-yellow-500",
    "무": "text-yellow-500",
    "기": "text-yellow-500",
    "진": "text-yellow-500",
    "술": "text-yellow-500",
    "축": "text-yellow-500",
    "미": "text-yellow-500",

    // Metal (Geum) - White/Gray
    "금": "text-gray-200",
    "경": "text-gray-200",
    "신": "text-gray-200",
    "유": "text-gray-200",

    // Water (Su) - Black/Dark Blue
    "수": "text-blue-400", // Using blue for visibility on dark bg
    "임": "text-blue-400",
    "계": "text-blue-400",
    "자": "text-blue-400",
    "해": "text-blue-400",
};

export const ELEMENT_BG_COLORS: Record<string, string> = {
    "목": "bg-green-900/20",
    "화": "bg-red-900/20",
    "토": "bg-yellow-900/20",
    "금": "bg-gray-800/40",
    "수": "bg-blue-900/20",
};

export const CHEONGAN_MAP: Record<string, string> = {
    "갑": "목", "을": "목",
    "병": "화", "정": "화",
    "무": "토", "기": "토",
    "경": "금", "신": "금",
    "임": "수", "계": "수"
};

export const JIJI_MAP: Record<string, string> = {
    "인": "목", "묘": "목",
    "사": "화", "오": "화",
    "진": "토", "술": "토", "축": "토", "미": "토",
    "신": "금", "유": "금",
    "해": "수", "자": "수"
};
