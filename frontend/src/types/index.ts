export interface Category {
  id: number;
  slug: string;
  name: string;
}
export interface Lesson {
  id: number;
  title: string;
  duration_minutes: number;
}
export interface Chapter {
  id: number;
  title: string;
  lessons: Lesson[];
}
export interface Course {
  id: number;
  slug: string;
  title: string;
  description: string;
  category: Category;
  difficulty: string;
  cover_kind: "web" | "javascript" | "python";
  lesson_count: number;
  chapter_count: number;
  duration_minutes: number;
  objectives?: string[];
  chapters?: Chapter[];
  enrolled?: boolean;
  summary?: LearningSummary;
}
export interface Pagination {
  page: number;
  per_page: number;
  total: number;
  pages: number;
}
export interface Enrollment {
  id: number;
  joined_at: string;
  available: boolean;
  course: Course;
  summary: LearningSummary | null;
}
export interface LearningSummary {
  completed_count: number;
  total_count: number;
  percent: number;
  completed_lesson_ids: number[];
  resume_lesson_id: number | null;
  state: "not_started" | "in_progress" | "quiz_required" | "completed";
  quiz_passed: boolean;
  latest_score: number | null;
  best_score: number | null;
}
export interface LearningData {
  course: Course;
  summary: LearningSummary;
  lesson: {
    id: number;
    course_id: number;
    chapter_id: number;
    title: string;
    body: string;
    video_url: string | null;
    duration_minutes: number;
    progress: { completed: boolean; video_position: number };
  };
}
export interface QuizData {
  id: number;
  course_id: number;
  course_title: string;
  title: string;
  version: number;
  pass_threshold: number;
  questions: {
    id: number;
    prompt: string;
    options: { id: string; text: string }[];
  }[];
  summary: LearningSummary;
}
export interface Attempt {
  id: number;
  course_id: number;
  title: string;
  course_title: string;
  version: number;
  score: number;
  correct_count: number;
  total_count: number;
  passed: boolean;
  submitted_at: string;
  answers?: {
    question_id: number;
    prompt: string;
    options: { id: string; text: string }[];
    correct_option_id: string;
    selected_option_id: string;
    is_correct: boolean;
    explanation: string;
  }[];
}
