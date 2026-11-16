export interface SignupRequest {
  full_name: string;
  email: string;
  password: string;
  institution?: string;
}

export interface SignupResponse {
  lecturer_id: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface ApiErrorResponse {
  detail: string | unknown[];
}

export interface LecturerResponse {
  id: number;
  full_name: string;
  email: string;
  institution: string | null;
}

export interface Course {
  id: number;
  course_code: string;
  course_name: string;
  department: string | null;
  level: string | null;
  student_count: number;
}

export type CoursesResponse = Course[];

export interface CreateCourseRequest {
  course_code: string;
  course_name: string;
  department?: string;
  level?: string;
}

export interface CreateCourseResponse {
  course_id: number;
}

export interface EnrollStudentRequest {
  matric_number: string;
}

export interface EnrollStudentResponse {
  status: string;
}

export interface CoursePathParams {
  course_id: number;
}

export interface CourseStudentPathParams extends CoursePathParams {
  matric_number: string;
}

export interface CourseStudent {
  matric_number: string;
  full_name: string;
  department: string | null;
  level: string | null;
  enrolled_at: string;
}

export type CourseStudentsResponse = CourseStudent[];

export interface UnenrollStudentResponse {
  status: string;
}

export interface RegisterStudentRequest {
  matric_number: string;
  full_name: string;
  department?: string;
  level?: string;
  samples: File[];
}

export interface RegisterStudentResponse {
  status: string;
  matric_number: string;
  samples_used: number;
}

export interface RecognizeFrameRequest {
  frame_file: File;
}

export type RecognitionStatus =
  | "marked"
  | "already_marked"
  | "spoof"
  | "unknown"
  | "not_enrolled";

export interface RecognitionFace {
  box: [number, number, number, number];
  status: RecognitionStatus;
  matric_number?: string;
  score?: number;
  label?: string;
}

export interface RecognizeFrameResponse {
  faces: RecognitionFace[];
}

export interface AttendanceRecord {
  matric_number: string;
  full_name: string;
  department: string | null;
  level: string | null;
  course_id: number;
  course_code: string;
  session_date: string;
  recorded_at: string;
}

export type AttendanceResponse = AttendanceRecord[];

export interface AttendanceQuery {
  session_date?: string;
}

export type RecognizeFramePathParams = CoursePathParams;
export type AttendancePathParams = CoursePathParams;

export interface ExportReportQuery {
  course_id?: number;
  session_date?: string;
}

export type ExportReportResponse = Blob;
