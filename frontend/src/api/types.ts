export type SignupRequest = {
  full_name: string
  email: string
  password: string
  institution?: string
}

export type SignupResponse = {
  lecturer_id: number | string
}

export type LoginRequest = {
  email: string
  password: string
}

export type LoginResponse = {
  access_token: string
  token_type: string
}

export type LecturerResponse = {
  id: number | string
  full_name: string
  email: string
  institution: string | null
}

export type Course = {
  id: number | string
  course_code: string
  course_name: string
  department: string | null
  level: string | number | null
  student_count: number
}

export type CreateCourseRequest = {
  course_code: string
  course_name: string
  department?: string
  level?: string | number
}

export type CreateCourseResponse = {
  course_id: number | string
}

export type EnrollStudentRequest = {
  matric_number: string
}

export type StatusResponse = {
  status: string
}

export type CourseStudent = {
  matric_number: string
  full_name: string
  department: string | null
  level: string | number | null
  enrolled_at: string
}

export type DeleteStudentResponse = StatusResponse

export type RegisterStudentRequest = {
  matric_number: string
  full_name: string
  department?: string
  level?: string | number
  samples: File[]
}

export type RegisterStudentResponse = {
  status: string
  matric_number: string
  samples_used: number
}

export type RecognitionStatus = 'marked' | 'already_marked' | 'spoof' | 'unknown' | 'not_enrolled'

export type RecognizedFace = {
  box: [number, number, number, number]
  status: RecognitionStatus
  matric_number?: string
  score?: number
  label?: string
}

export type RecognizeFrameRequest = {
  frame_file: File
}

export type RecognizeResponse = {
  faces: RecognizedFace[]
}

export type AttendanceRecord = {
  matric_number: string
  full_name: string
  department: string | null
  level: string | number | null
  course_id: number | string
  course_code: string
  session_date: string
  recorded_at: string
}

export type AttendanceQuery = {
  session_date?: string
}

export type ExportReportRequest = {
  course_id?: number | string
  session_date?: string
}

// The endpoint returns an .xlsx file; its successful response is read as a Blob.
export type ExportReportResponse = Blob

export type ApiErrorResponse = {
  detail: string | unknown[]
}
