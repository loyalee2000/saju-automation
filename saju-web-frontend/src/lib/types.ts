export interface SajuFormData {
    name: string;
    gender: "male" | "female";
    year: string;
    month: string;
    day: string;
    hour: string;
    minute: string;
    timeUnknown: boolean;
    calendarType: "solar" | "lunar";
    isLeapMonth: boolean;
    location: string;
}

export interface SajuResult {
    info: {
        name: string;
        gender: string;
        solar_date?: { year: number; month: number; day: number; hour: number; minute: number };
        lunar_date?: { year: number; month: number; day: number };
        ddi?: string;
        age?: number;
    };
    four_pillars: {
        year: { gan: string; ji: string };
        month: { gan: string; ji: string };
        day: { gan: string; ji: string };
        hour: { gan: string; ji: string };
    };
    five_elements: {
        "목(Tree)": number;
        "화(Fire)": number;
        "토(Earth)": number;
        "금(Metal)": number;
        "수(Water)": number;
        [key: string]: number;
    };
    daewoon: {
        direction: string;
        pillars: {
            age: number;
            end_age: number;
            end_year: number;
            ganji: string;
            year: number;
            seun?: {
                year: number;
                age: number;
                ganji: string;
                monthly_luck: string;
            }[];
        }[];
    };

    // Flattened structure from API v2.7
    gongmang: string[] | string;
    twelve_unseong: {
        year: { stage: string };
        month: { stage: string };
        day: { stage: string };
        hour: { stage: string };
    };
    jijanggan: { year: string[]; month: string[]; day: string[]; hour: string[] };
    nabeum: { year: string; month: string; day: string; hour: string };
    sinsal: {
        year: { gan: string[]; ji: string[] };
        month: { gan: string[]; ji: string[] };
        day: { gan: string[]; ji: string[] };
        hour: { gan: string[]; ji: string[] };
    };

    // Optional / Legacy / Extra Details
    sibseong?: any;
    sibseong_details?: any;
    sinsal_details?: any;
    interactions?: any;
    interaction_details?: any;
    strength?: any;
    gyeokguk?: any;
    yongsin_structure?: any;
    health_analysis?: any;

    // Keep derived optional for compatibility if older backend is valid
    derived?: any;
}
