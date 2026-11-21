# Frontend task prompts

One prompt per Copilot session, run in order. Merge each pull request before starting the next, so the agent sees the earlier work.

Before Task 1, `.github/copilot-instructions.md` must already be on the `main` branch.

Each prompt below is meant to be pasted whole. They all end with the same line asking for a pull request.

---

## Task 1: Scaffold and design tokens

```
Set up the frontend in a new `frontend/` folder. Do not touch the Python code at the repo root.

- Scaffold Vite + React + TypeScript with strict mode on.
- Add Tailwind CSS and initialise shadcn/ui. Install only these components for now: button, input, label, dialog, table, badge, skeleton.
- Add react-router-dom and @tanstack/react-query.
- Implement the design tokens from the instructions as CSS variables. Dark theme is the default, light theme is toggled by a class. Wire the Tailwind theme to the variables.
- Load Inter and Space Grotesk through @fontsource packages.
- Create src/lib/capture.ts with the capture constants from the instructions.
- Create src/api/types.ts with a TypeScript type for every request and response in the API contract.
- Add frontend/.env.example with VITE_API_URL.
- Add a temporary page at "/" that shows the colour palette, the type scale, every button variant, and the three status colours, so I can check the design.

Acceptance: build and lint pass, the palette page renders in dark and light, and no Vite demo content is left.
Out of scope: auth and real pages.

Open a pull request titled "Task 1: scaffold and design tokens".
```

---

## Task 2: API client, auth, routing

```
Add the shared infrastructure. No real screens yet, placeholder pages are fine.

1. src/api/client.ts: a typed fetch wrapper that uses VITE_API_URL and attaches the Authorization header from the token store. It parses { detail } error bodies into an ApiError class carrying status and message. It supports JSON, multipart FormData (do not set Content-Type yourself), and blob responses. On a 401 from any request except the login call, it clears the token and notifies the auth context.
2. src/auth/AuthContext.tsx: holds the token (localStorage key "attendance_token") and exposes login, signup, logout, isAuthenticated, and the current lecturer (fetched from GET /auth/me once a token is present). Decode the JWT payload without verifying it, only to read "exp" and clear an expired token on load.
3. src/routes/ProtectedRoute.tsx: redirects to /login and remembers the intended destination.
4. Routes: /signup, /login, /dashboard, /courses/:courseId, /students/register, /session/:courseId, /reports. "/" redirects to /dashboard.
5. A QueryClientProvider with sensible defaults, and no retry on 4xx errors.
6. Hooks in src/api/hooks for every endpoint in the contract: current lecturer, courses list, create course, roster, enroll, unenroll, attendance list. Plus plain functions for login, signup, register student, recognize frame, and export download.
7. Vitest tests for client.ts covering the auth header, error parsing, and 401 handling.

Acceptance: build, lint and tests pass. Visiting a protected route while logged out redirects to /login.

Open a pull request titled "Task 2: API client and auth plumbing".
```

---

## Task 3: Signup and login screens

```
Build /signup and /login using the design system.

- A centred single card with the app wordmark above it.
- Signup fields: full name, email, password, institution (optional). Login fields: email and password.
- Client-side validation: valid email, password of at least 8 characters. Show field-level errors, and show the server "detail" message in an inline alert.
- Signup success navigates to /login with a success toast and the email prefilled. Login success navigates to the originally intended route, or /dashboard.
- Disable the submit button while pending and show a spinner. Enter submits. Focus the first field on load. Use correct autocomplete attributes. Add a show/hide password toggle.
- A wrong password must show the server message. It must NOT trigger the logout flow.
- If already logged in, visiting /login or /signup redirects to /dashboard.

Acceptance: build and lint pass, and both screens work with keyboard only.

Open a pull request titled "Task 3: signup and login".
```

---

## Task 4: App shell and dashboard

```
Build the app shell and the dashboard.

Shell: a collapsible sidebar with Dashboard, Register student and Reports links, then the lecturer's name and institution (from GET /auth/me) above a logout button at the bottom. A top bar shows the page title. On small screens the sidebar becomes a drawer. Add a dark/light theme toggle. Highlight the active route.

Dashboard (/dashboard):
- A greeting with the lecturer's first name, a heading "Courses", stat tiles for the number of courses and total enrolments (the sum of student_count, labelled "Enrolments" because a student in two courses counts twice), and an "Add course" button.
- A course list. Each row shows course code, name, department and level, and student count. A "Start session" button goes to /session/:id. Clicking the row goes to /courses/:id.
- "Add course" opens a dialog (code, name, department, level) that posts to POST /courses. On success, invalidate the list and show a toast. Show a duplicate-code error inline.
- Loading skeleton, an empty state with a clear call to action, and an error state with a retry.
- Do not show recent sessions or a count of unique students. The API does not provide them. Leave TODO(backend) comments where they would go.

Acceptance: build and lint pass, and layout works from 375px wide to desktop.

Open a pull request titled "Task 4: app shell and dashboard".
```

---

## Task 5: Course detail

```
Build /courses/:courseId.

- Look the course up in the list from GET /courses. If it is not found, show a not-found state with a link back to the dashboard.
- Header with course code and name, a "Start session" button, and an "Export to Excel" button that downloads using the authenticated blob approach from the instructions.
- Roster table (GET /courses/{id}/students): matric number, name, department, level, and a remove button. Removing asks for confirmation in a dialog, then calls the DELETE endpoint with the matric number URL-encoded.
- An "Enroll student" form (matric number) that posts to the enroll endpoint. Show the server's 400 message inline (for example the student is not registered under this lecturer, or is already enrolled). Invalidate the roster on success.
- Attendance history table (GET /attendance/{id}) with an optional date filter. Columns: date, matric number, name, time checked in (derived from recorded_at).
- Loading, empty and error states for each table.

Acceptance: build and lint pass, and every mutation refreshes the relevant table.

Open a pull request titled "Task 5: course detail".
```

---

## Task 6: Register student (camera)

```
Build /students/register.

Flow:
1. A form: matric number, full name, department (optional), level (optional).
2. A camera panel with a mirrored live preview. Request the camera only when the user clicks "Start camera". Show distinct messages for permission denied, no camera found, and insecure context.
3. A "Capture samples" button. It grabs a JPEG frame every REGISTER_SAMPLE_INTERVAL_MS until it has REGISTER_SAMPLE_COUNT frames, using the capture rules in the instructions (un-mirrored, CAPTURE_WIDTH, JPEG_QUALITY). Show a progress bar and "Sample n of N", plus short guidance: look at the camera, turn your head slightly, keep the face well lit.
4. Submit everything in ONE multipart request to POST /students/register, with the form fields and each frame appended as a "samples" file.
5. Result states: success (show samples_used and a "Register another student" button) or failure (show the server detail; for the "no valid, live face samples" error give retry tips and keep the form values so the user can capture again without retyping).

Rules: stop all camera tracks after submit, on error, and on leaving the page. Disable submit until all frames are captured. Prevent double submission.

Camera behaviour cannot be tested in the cloud environment. Say so in the PR description and list what should be tested manually.

Open a pull request titled "Task 6: register student".
```

---

## Task 7: Live session

```
Build /session/:courseId, the main screen of the app. Make it feel calm and polished.

Layout: a large camera preview with a transparent overlay canvas on top, and a side panel (below the video on small screens).

Side panel:
- Stats: marked this session, enrolled (from the roster length), attendance rate, and an elapsed-time timer.
- A "Checked in" feed, newest first, with name and time. Get names by mapping matric_number to the roster (GET /courses/{courseId}/students).
- A legend for the box colours.

Controls: a "Start session" button (starts the camera and polling) and an "End session" button. Ending stops polling, stops camera tracks, and opens a summary dialog (number marked, duration, the list) with buttons for "View attendance" (course detail) and "Export to Excel".

Polling: every RECOGNIZE_INTERVAL_MS, capture a frame per the instructions and POST it to /attendance/{courseId}/recognize. Never send a new request while one is in flight.

Overlay: draw one box per returned face, scaled from uploaded-frame pixels to displayed size (and mirrored the same way as the preview if the preview is mirrored). Colours: marked = success, already_marked = warning, spoof / unknown / not_enrolled = danger. Label each box with the student's name (or matric number), or "Spoof", "Unknown", "Not enrolled".

Counting: add a student to the feed and the marked count only the first time a "marked" status comes back for them. "already_marked" is shown on the box but not counted.

Errors: on a transient network failure show a "Reconnecting..." banner and keep trying with backoff. A 401 follows the normal logout flow. Use aria-live for new check-ins.

Camera behaviour cannot be tested in the cloud environment. Say so in the PR description and list what should be tested manually.

Open a pull request titled "Task 7: live session".
```

---

## Task 8: Reports

```
Build /reports.

- A course select (from GET /courses) and an optional date input (type=date, sent as YYYY-MM-DD).
- A dense attendance table (GET /attendance/{courseId}?session_date=...) with client-side sorting and a sticky header. It needs a selected course, so show a prompt until one is chosen. Columns: date, matric number, name, department, level, time checked in.
- An "Export to Excel" button using the authenticated blob download from the instructions. With a course selected it exports that course (and the date, if set). With no course selected, label it "Export all courses" and call the endpoint with no filters.
- A 404 from the export endpoint means there is nothing to export. Show its message as a friendly toast, not an error screen.
- Loading, empty and error states.

Acceptance: build and lint pass, and the downloaded file opens as .xlsx.

Open a pull request titled "Task 8: reports".
```

---

## Task 9: Polish and QA pass

```
Review the whole app and fix problems. Do not add features.

- Every data screen has a loading skeleton, an empty state with a next action, and an error state with retry.
- Keyboard navigation works everywhere, focus rings are visible, and form labels are correct.
- Text contrast meets the token rules in the instructions, in both themes.
- The layout works from 375px wide to desktop. Spacing follows the 8px grid.
- Add a 404 page and set page titles and a favicon.
- Remove unused dependencies, components and dead code.
- Write frontend/README.md covering setup, environment variables, scripts, and the project structure.
- Add a "Project status" section to .github/copilot-instructions.md listing what is built.

Open a pull request titled "Task 9: polish and QA".
```

---

## Fix-up comments for pull requests

When a result is close but not right, comment on the pull request instead of starting a new session. Examples:

```
The spacing on the dashboard rows does not follow the 8px grid. Use p-4 for row padding and gap-2 between rows, and align the buttons to the right edge.
```

```
The overlay boxes are offset from the faces. Scale each box using (video.clientWidth / uploadedFrameWidth) and (video.clientHeight / uploadedFrameHeight), and mirror the x coordinates if the preview is mirrored.
```

```
Two components duplicate the same status badge logic. Extract one <StatusBadge status="..."> component and use it in both places.
```
