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
}
