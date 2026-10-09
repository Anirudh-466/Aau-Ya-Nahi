# AAU YA NAHI! — SMART STUDENT ATTENDANCE MANAGER 🎓

> **"Your Attendance. Your Choice. Your Call."**

**Aau ya Nahi!** is a modern, responsive, student-friendly web application designed to help college students track, manage, analyze, and optimize their class attendance.

It answers the everyday dilemma of every college student:
> *"Aau ya nahi? Aur agar nahi aau, toh attendance kitni rahegi?"*

---

## 🌟 Key Features

### 1. 🧮 The Bunk Calculator (Core Mathematical Engine)
- **How Many Classes Can I Skip?**
  Accurately calculates the maximum consecutive future classes you can safely miss while remaining above your target percentage $T$.
  $$\text{Max Skippable Classes} = \left\lfloor \frac{100 \times A}{T} - C \right\rfloor$$
- **How Many Classes Must I Attend?**
  Calculates the minimum consecutive classes needed to recover and achieve your target:
  $$\text{Required Classes} = \left\lceil \frac{T \times C - 100 \times A}{100 - T} \right\rceil$$
- **Live What-If Simulation:**
  Interactive steppers allowing you to test: *"If I attend $X$ and miss $Y$ upcoming classes, what will my attendance be?"*
- **Edge Case Protection:**
  Handles 0 conducted classes, 100% target limits, and prevents negative bunk recommendations.

### 2. 📊 Student Dashboard
- **Overall Attendance Metric:**
  Calculated strictly as $\frac{\text{Total Attended}}{\text{Total Conducted}} \times 100$ (never an inaccurate simple average of percentages).
- **Attendance Status Badges:**
  - `Target Achieved` (Emerald)
  - `Safe` (Teal / Blue)
  - `Near Target` (Amber)
  - `Below Target` (Rose)
- **Visual Analytics:**
  Dynamic chart comparing each subject's current percentage against personal targets and the 75% institutional requirement line.
- **"Aau ya Nahi?" Decision Assistant:**
  Context-aware advice recommending whether you should attend or can take a break for today's classes.

### 3. 📚 Complete Subject Management
- Add, edit, and delete subjects with full input validation (conducted $\ge$ attended $\ge 0$).
- Single-tap **+1 Present** and **+1 Absent** quick buttons on each card.
- Subject details drawer showing full historical attendance logs and individual faculty information.

### 4. 📅 Attendance Log & History
- Detailed chronological log of every recorded class session.
- Filter by Subject, Date, and Attendance Status (Present / Absent).
- Add session notes (e.g. topics covered, lab exams, reasons for absence).
- Inline editing and deletion with automatic recalculation of subject counters.

### 5. 📈 Reports & CSV Export
- Printable academic report summary.
- One-click CSV export of all subjects and historical logs.

### 6. 🌓 Dual Theme Architecture (Dark & Light Mode)
- Full dark mode using deep navy and charcoal tones with high-contrast text.
- Clean light mode with subtle academic stationery and formula background patterns.
- Persistent user preference across sessions.

### 7. 🔒 Secure Authentication & Data Persistence
- Seamlessly supports **Supabase PostgreSQL** with Row Level Security (RLS) policies.
- Built-in **Offline / Local Demo Mode** with realistic sample subjects so anyone can immediately run and test the app with zero setup hurdles.

---

## 📐 Mathematical Verification of Prompt Scenarios

All scenarios are verified through our automated Vitest unit test suite (`src/utils/calculator.test.ts`):

| Scenario | Conducted ($C$) | Attended ($A$) | Current % | Target ($T$) | Result |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Scenario 1** | 20 | 16 | 80.00% | 75% | **Can skip 1 class** $\lfloor(100 \times 16 / 75) - 20\rfloor = 1$ |
| **Scenario 2** | 20 | 12 | 60.00% | 75% | **Must attend 12 classes** $\lceil(75 \times 20 - 100 \times 12) / 25\rceil = 12$ |
| **Scenario 3** | 10 | 10 | 100.00% | 75% | **Can skip 3 classes** $\lfloor(100 \times 10 / 75) - 10\rfloor = 3$ |
| **Scenario 4** | 10 | 6 | 60.00% | 75% | **Must attend 6 classes** $\lceil(75 \times 10 - 100 \times 6) / 25\rceil = 6$ |

---

## 🛠️ Technology Stack

- **Frontend:** React 18, TypeScript, Tailwind CSS, Vite
- **Icons:** Lucide React
- **Charts:** Recharts
- **Testing:** Vitest
- **Backend / Database:** Supabase PostgreSQL with RLS (with automatic Local Storage fallback)

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Node.js (v18 or higher)
- npm or pnpm

### 2. Installation
```bash
# Clone the repository and navigate to the directory
cd "MINI PROJECT AIML"

# Install dependencies
npm install
```

### 3. Run Development Server
```bash
npm run dev
```
Open your browser at `http://localhost:5173`.

### 4. Run Test Suite
```bash
npm run test
```

### 5. Production Build
```bash
npm run build
```

---

## 🗄️ Supabase Cloud Database Setup (Optional)

If you wish to synchronize data to your Supabase PostgreSQL cloud database:

1. Create a project at [supabase.com](https://supabase.com).
2. Go to the **SQL Editor** in your Supabase dashboard.
3. Open `supabase/schema.sql` from this repository and run the SQL script to create tables, indexes, RLS policies, and triggers.
4. Copy your project URL and public Anon key from **Project Settings > API**.
5. Create a `.env` file in the root directory:
   ```env
   VITE_SUPABASE_URL=https://your-project-id.supabase.co
   VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
   ```
6. Restart Vite (`npm run dev`). The application will automatically detect Supabase and connect!

---

## 📱 Mobile Friendly
Fully responsive layout tested across mobile viewports, tablets, and desktop displays with touch-friendly tap targets and collapsible navigation.
