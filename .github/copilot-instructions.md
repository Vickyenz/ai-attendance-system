# Frontend instructions: AI attendance system


## Project

A web app where lecturers sign up, create courses, register students by face, and run live attendance sessions using a webcam. The backend is FastAPI (Python) and already built. The frontend you are building lives in `frontend/`.

**Do not modify** the Python folders at the repo root (`app/`, `src/`), nor `data/`, `models/`, or any `.env` file.

## Stack

- Vite, React, TypeScript (strict mode)
- Tailwind CSS and shadcn/ui (install a component only when it is used)
- React Router and TanStack Query
- A typed `fetch` wrapper for HTTP
- Do not add other dependencies unless essential. List any you add in the PR description.

## Environment

- `VITE_API_URL` defaults to `http://localhost:8000`. Provide `frontend/.env.example`. Never hardcode the URL. Never commit `.env`.
- The JWT is stored in localStorage under the key `attendance_token` (accepted trade-off for v1).

## API contract

All endpoints except `/auth/*` need the header `Authorization: Bearer <token>`. Errors come back as `{ "detail": string }`. A 422 returns `detail` as an array, so show a generic message for that case.

| Method and path | Request | Response |
|---|---|---|
| `POST /auth/signup` | JSON `{ full_name, email, password, institution? }` | 201 `{ lecturer_id }` |
| `POST /auth/login` | JSON `{ email, password }` | `{ access_token, token_type }`, or 401 with a message |
| `GET /auth/me` | none | `{ id, full_name, email, institution }`, or 401 |
| `GET /courses` | none | `[{ id, course_code, course_name, department, level, student_count }]` |
| `POST /courses` | JSON `{ course_code, course_name, department?, level? }` | `{ course_id }`, or 400 on duplicate code |
| `POST /courses/{course_id}/enroll` | JSON `{ matric_number }` | 201 `{ status }`, or 400 with a message |
| `GET /courses/{course_id}/students` | none | `[{ matric_number, full_name, department, level, enrolled_at }]` |
| `DELETE /courses/{course_id}/students/{matric_number}` | none | `{ status }`, or 404 |
| `POST /students/register` | multipart: `matric_number`, `full_name`, `department?`, `level?`, and one or more `samples` files (JPEG) | 201 `{ status, matric_number, samples_used }`, or 400 with a message |
| `POST /attendance/{course_id}/recognize` | multipart: one `frame_file` (JPEG) | `{ faces: [{ box: [x1,y1,x2,y2], status, matric_number?, score?, label? }] }` |
| `GET /attendance/{course_id}?session_date=YYYY-MM-DD` | none | `[{ matric_number, full_name, department, level, course_id, course_code, session_date, recorded_at }]` |
| `GET /reports/export?course_id=&session_date=` | none | an `.xlsx` file, or 404 with a message if there is nothing to export |

`status` in a recognize result is one of: `marked`, `already_marked`, `spoof`, `unknown`, `not_enrolled`.

### Behaviour rules

- A 401 on any protected request clears the token and redirects to `/login`. The login request itself is the exception: show its error message instead.
- Matric numbers can contain `/` (for example `AFIT/22/1040`). Wrap them in `encodeURIComponent` when building URL paths.
- **The export endpoint is protected**, so a plain `<a href>` cannot work. Fetch it with the auth header, read `response.blob()`, create an object URL, and trigger the download. Use the filename from `Content-Disposition`, with a fallback.

## Not available from the API yet

Do not invent these. Render only what the API returns, and leave a `// TODO(backend):` comment where the UI would go.

- A list of recent sessions.
- A count of unique students across all courses. Summing `student_count` over courses counts enrolments (a student in two courses counts twice), so label that figure "Enrolments".
- `GET /courses/{id}` for a single course. Look the course up in the list from `GET /courses`.

## Camera and capture

Constants live in `src/lib/capture.ts`:

```ts
export const CAPTURE_WIDTH = 640;
export const JPEG_QUALITY = 0.8;
export const RECOGNIZE_INTERVAL_MS = 1000;
export const REGISTER_SAMPLE_COUNT = 20;
export const REGISTER_SAMPLE_INTERVAL_MS = 400;
```

These match the values used when the face-recognition thresholds were calibrated. Do not change them without saying so in the PR description.

- Capture a frame by drawing the `<video>` onto an offscreen canvas at `CAPTURE_WIDTH` (height from the aspect ratio), then `toBlob('image/jpeg', JPEG_QUALITY)`. Capture un-mirrored, even if the preview is mirrored.
- Bounding boxes from `/recognize` are `[x1, y1, x2, y2]` in pixels of the **uploaded** frame. Scale them to the displayed video size. If the preview is mirrored with CSS, mirror the overlay the same way.
- Never send a recognize request while the previous one is still in flight.
- Run the capture loop as an awaited async loop, not `setInterval`: capture, upload, await the response, then wait `max(0, RECOGNIZE_INTERVAL_MS - elapsed)` before the next frame. Cancel it with an `AbortController`.
- Size the video container to the camera's aspect ratio (from `videoWidth` and `videoHeight`) and avoid `object-fit: cover`, so box scaling is simply displayed width divided by uploaded frame width.
- Draw the overlay on a canvas from the latest response (keep it in a ref, not React state), and clear boxes older than about 1.5 seconds so stale boxes never linger.
- Stop all camera tracks (`track.stop()`) on unmount, on route change, and when a session ends.
- `getUserMedia` needs HTTPS or localhost. Show distinct, clear messages for permission denied, no camera found, and insecure context.

## Design system

Dark theme is the default. Light theme is secondary and toggled by a class. Define everything as CSS variables and wire Tailwind to them.

| Token | Dark | Light |
|---|---|---|
| background | `#0F1620` | `#FAFAF8` |
| surface | `#161F2C` | `#FFFFFF` |
| border (1px hairline) | `#2A3542` | `#E2E0D8` |
| accent (button fills, active states) | `#0F6E56` | `#0F6E56` |
| accent-fg (links and text on dark) | `#4FD1B0` | `#0F6E56` |
| success / marked | `#10B981` | `#047857` |
| warning / already marked | `#D97706` | `#B45309` |
| danger / spoof, unknown, not enrolled | `#DC2626` (borders, fills) | `#B91C1C` |
| danger-fg (text on dark) | `#F87171` | `#B91C1C` |

The accent `#0F6E56` is too dim for text on the dark background, so use `accent-fg` for text and links there. Use `danger-fg` for red text. Status colors are only for attendance and recognition states, nowhere else. There is one accent colour: no purple, no gradients.

**Typography:** Inter for UI text. Space Grotesk for headings, numbers and stats. Load both through `@fontsource` packages (no external requests). Use a restrained type scale. This is a daily-use tool, not a landing page.

**Layout:** 8px spacing grid. Collapsible sidebar plus main content (a drawer on small screens). Dense, legible tables. Cards use hairline borders, not shadows. Border radius 6 to 8px.

**Avoid:** generic untouched shadcn gray, gradients, glassmorphism, blur, drop shadows, bubble corners, decorative blobs, oversized hero headings, lorem ipsum.

## Code conventions

- Folders: `src/api`, `src/auth`, `src/components/ui` (shadcn), `src/components`, `src/features/<name>`, `src/lib`, `src/pages`, `src/routes`.
- Function components with named exports. No `any`. Small components.
- Server data goes through TanStack Query, with query keys per resource. Invalidate after mutations.
- Every screen that loads data has a loading skeleton, an empty state with a clear next action, and an error state with a retry button.
- Forms are accessible: labels, correct `autocomplete`, visible focus rings, keyboard operable. Use `aria-live` for session status updates.
- Sample or test data uses realistic Nigerian names, course codes like `MCE 301`, and matric numbers like `AFIT/22/1040`.

## Definition of done

- `npm run build` and `npm run lint` pass. No TypeScript errors and no console errors in dev.
- The PR description lists what was built, which files changed, any added dependencies, and anything that could not be verified. Camera behaviour cannot be tested in the cloud environment, so say so for camera tasks.
- One task per pull request.
