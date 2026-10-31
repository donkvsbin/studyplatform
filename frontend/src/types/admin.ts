export interface AdminLesson {
  id: number;
  title_zh: string;
  title_en: string;
  body_zh: string;
  body_en: string;
  video_url: string | null;
  duration_minutes: number;
  sort_order: number;
  archived: boolean;
}
export interface AdminChapter {
  id: number;
  title_zh: string;
  title_en: string;
  sort_order: number;
  archived: boolean;
  lessons: AdminLesson[];
}
export interface AdminCourse {
  id: number;
  slug: string;
  title_zh: string;
  title_en: string;
  description_zh: string;
  description_en: string;
  objectives_zh: string[];
  objectives_en: string[];
  category_id: number;
  difficulty: string;
  status: string;
  archived: boolean;
  chapters: AdminChapter[];
}
export interface AdminQuestion {
  id?: number;
  prompt_zh: string;
  prompt_en: string;
  explanation_zh: string;
  explanation_en: string;
  options: { id: string; text_zh: string; text_en: string }[];
  correct_option_id: string;
  sort_order: number;
  archived?: boolean;
}
export interface AdminQuiz {
  id: number;
  title_zh: string;
  title_en: string;
  version: number;
  questions: AdminQuestion[];
}
