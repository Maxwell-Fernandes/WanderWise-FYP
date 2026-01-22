# WanderWise+ Frontend MVP Structure

## Complete Application Flow

### 🏠 Page 1: Landing Page (`/`)
**Status: ✅ Complete**
- **Layout**: Hero section with gradient background
- **Components**:
  - Navigation bar with logo and auth buttons
  - Large title "WanderWise+" with gradient text
  - Subtitle explaining AI-powered route planning
  - 4 feature cards (AI Recommendations, Smart Routes, Personalized Schedules, Research-Backed)
  - "How It Works" section with 4 numbered steps
  - Stats section (100+ locations, Save Hours, AI Powered)
  - Footer with copyright

**Visual Design**:
- Ocean blue (#0277BD) and sunset orange (#FF6F00) theme
- Responsive grid layout
- Card-based UI with hover effects
- Call-to-action buttons (Get Started / Sign In)

---

### 🔐 Page 2: Login (`/login`)
**Status: ✅ Complete**
- **Layout**: Centered card with gradient background
- **Components**:
  - Logo icon in circular gradient
  - Email and password inputs with icon prefixes
  - Remember me checkbox
  - Forgot password link
  - Demo credentials display box
  - Link to registration page
- **Functionality**: Mock authentication (any credentials work)

---

### 📝 Page 3: Register (`/register`)
**Status: 🔨 Needs Update**
- **Layout**: Similar to login but with more fields
- **Components**:
  - Full name input
  - Email input
  - Password input with strength indicator
  - Confirm password input
  - Terms and conditions checkbox
  - Sign up button
  - Link back to login

---

### ✨ Page 4: Interest Input (`/interests`)
**Status: ✅ Complete**
- **Layout**: Full-width with centered max-width container
- **Components**:
  - Header with sparkles icon
  - Large textarea for natural language input
  - Character counter (0/500)
  - "Analyze with AI" button with loading state
  - Example prompts grid (4 clickable examples)
  - Analysis results card with:
    - Interest bars showing confidence scores
    - Color-coded (green high, blue medium, yellow low)
    - Continue button

**Module Info**: Module I - NLC (Natural Language Classification)

---

### 📅 Page 5: Itinerary Form (`/create-itinerary`)
**Status**: 🔨 Needs Complete Redesign with Tailwind
- **Layout**: Centered form card
- **Components**:
  - Number of days selector (1-7, visual slider)
  - Start date picker (calendar widget)
  - Daily start time picker
  - Daily end time picker
  - Budget category selector (3 buttons: Budget, Moderate, Luxury)
  - Generate itinerary button with loading animation
  - Progress indicator showing Modules II-IV

**Module Info**: Modules II-IV (POI Selection, K-Means Clustering, Genetic Algorithm)

---

### 🗺️ Page 6: Itinerary View (`/itinerary/:id`)
**Status**: 🔨 Needs Creation
- **Layout**: Split view - tabs on left, map on right
- **Components**:
  **Left Panel (60%)**:
  - Summary card (3 days, 145.6 km, 6 stops total)
  - Day tabs (Day 1, Day 2, Day 3)
  - Timeline for selected day:
    - Vertical timeline with dots
    - Place cards showing:
      - Arrival/departure times
      - Place name and category
      - Duration
      - Travel time to next
      - Entry fee badge

  **Right Panel (40%)**:
  - Interactive map with:
    - Place markers (colored by cluster)
    - Route lines between places
    - Popup on marker click
    - Zoom controls

  **Bottom Actions**:
  - "Submit Feedback Survey" button
  - "Export PDF" button (future)
  - "Share Itinerary" button (future)

---

### 📊 Page 7: Survey Form (`/survey/:id`)
**Status**: 🔨 Needs Creation
- **Layout**: Form with sections
- **Components**:
  - Header explaining research evaluation
  - Likert scale questions (P1-P14):
    - 5-point scale (Strongly Disagree to Strongly Agree)
    - Radio buttons with labels
    - Each question in its own card
  - Text response questions (P15-P16):
    - "What did you like most?"
    - "What improvements would you suggest?"
    - Large text areas
  - Submit button
  - Success message on completion

---

## Component Architecture

### UI Components (`src/components/ui/`)
✅ **Button.jsx** - Variants: default, outline, secondary, ghost, link
✅ **Card.jsx** - Card, CardHeader, CardTitle, CardDescription, CardContent
✅ **Input.jsx** - Styled input fields with focus states
✅ **Label.jsx** - Form labels

### Feature Components
✅ **Navigation.jsx** - Responsive navbar with mobile menu
✅ **Home.jsx** - Landing page
✅ **Login.jsx** - Authentication form
✅ **InterestInput.jsx** - NLP text input with analysis
🔨 **Register.jsx** - Sign up form (needs Tailwind update)
🔨 **ItineraryForm.jsx** - Trip configuration (needs Tailwind update)
🔨 **ItineraryView.jsx** - Full itinerary display (needs creation)
🔨 **DaySchedule.jsx** - Daily timeline component (needs creation)
🔨 **InteractiveMap.jsx** - MapLibre GL JS map (needs creation)
🔨 **SurveyForm.jsx** - P1-P16 questions (needs creation)

### State Management (`src/stores/`)
- **authStore.js** - User authentication state
- **itineraryStore.js** - Itinerary and interests state

### Mock Data (`src/data/`)
✅ **mockData.js** - Sample places, itinerary, and survey questions

---

## Design System

### Colors
- **Primary**: #0277BD (Ocean Blue)
- **Secondary**: #FF6F00 (Sunset Orange)
- **Background**: #FFFFFF
- **Muted**: #F3F4F6
- **Border**: #E5E7EB
- **Success**: Green-500
- **Warning**: Yellow-500
- **Error**: Red-500

### Typography
- **Font**: System font stack
- **Headings**: Bold, large sizes
- **Body**: Regular weight, readable sizes
- **Captions**: Smaller, muted colors

### Spacing
- **Containers**: max-w-4xl to max-w-6xl
- **Cards**: p-6 to p-8
- **Gaps**: space-y-4 to space-y-8

### Responsive Breakpoints
- **Mobile**: < 768px (stacked layout)
- **Tablet**: 768px - 1024px (partial grid)
- **Desktop**: > 1024px (full grid layout)

---

## Technical Stack

### Core
- **React 19** - UI library
- **Vite 7** - Build tool
- **React Router 7** - Client-side routing
- **Zustand 5** - State management

### Styling
- **Tailwind CSS 4** - Utility-first CSS
- **Tailwind Vite Plugin** - v4 integration
- **Lucide React** - Icon library
- **CVA** - Class variance authority for component variants

### Maps (Planned)
- **MapLibre GL JS** - Open-source maps
- **react-map-gl** - React wrapper

### Forms (Planned)
- **date-fns** - Date manipulation

---

## Next Steps to Complete MVP

### High Priority
1. **Create/Update Remaining Pages with Tailwind**:
   - ✅ Login
   - ✅ Home
   - ✅ Interest Input
   - 🔨 Register (update from MUI to Tailwind)
   - 🔨 Itinerary Form (update from MUI to Tailwind)
   - 🔨 Itinerary View (create new)
   - 🔨 Survey Form (create new)

2. **Add Interactive Map**:
   - Install maplibre-gl
   - Create InteractiveMap component
   - Add markers for places
   - Draw route lines between places

3. **Polish Responsive Design**:
   - Test on mobile devices
   - Ensure all cards stack properly
   - Fix any overflow issues

### Medium Priority
4. **Add Micro-interactions**:
   - Button hover effects
   - Card lift on hover
   - Smooth transitions
   - Loading animations

5. **Improve Accessibility**:
   - ARIA labels
   - Keyboard navigation
   - Focus indicators
   - Screen reader support

### Low Priority
6. **Optional Enhancements**:
   - Dark mode toggle
   - Export to PDF
   - Share itinerary link
   - Save itinerary to account

---

## File Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/
│   │   │   ├── button.jsx ✅
│   │   │   ├── card.jsx ✅
│   │   │   ├── input.jsx ✅
│   │   │   └── label.jsx ✅
│   │   ├── Auth/
│   │   │   ├── Login.jsx ✅
│   │   │   └── Register.jsx 🔨
│   │   ├── Common/
│   │   │   └── Navigation.jsx ✅
│   │   ├── Interests/
│   │   │   └── InterestInput.jsx ✅
│   │   ├── Itinerary/
│   │   │   ├── ItineraryForm.jsx 🔨
│   │   │   ├── ItineraryView.jsx 🔨
│   │   │   └── DaySchedule.jsx 🔨
│   │   ├── Map/
│   │   │   └── InteractiveMap.jsx 🔨
│   │   └── Feedback/
│   │       └── SurveyForm.jsx 🔨
│   ├── pages/
│   │   └── Home.jsx ✅
│   ├── stores/
│   │   ├── authStore.js ✅
│   │   └── itineraryStore.js ✅
│   ├── data/
│   │   └── mockData.js ✅
│   ├── lib/
│   │   └── utils.js ✅
│   ├── App.jsx ✅
│   ├── main.jsx ✅
│   └── index.css ✅
├── public/
├── package.json ✅
├── vite.config.js ✅
└── index.html ✅
```

---

## Current Server
**Running on**: http://localhost:5175/

## Testing Instructions
1. Navigate to home page
2. Click "Sign In" → Enter any credentials
3. View Interest Input → Type preferences → Analyze
4. Continue to Itinerary Form (needs completion)
5. Generate itinerary (needs completion)
6. View full itinerary with map (needs completion)
7. Submit feedback survey (needs completion)
