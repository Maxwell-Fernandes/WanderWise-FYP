# WanderWise+ Frontend

React-based frontend for the WanderWise+ intelligent tourism route planning system.

## Features

### 1. User Authentication
- Registration with email and password
- Login with JWT token authentication
- Protected routes for authenticated users
- Automatic token refresh

### 2. Interest Input (Module I - NLC)
- Natural language text input for user preferences
- Example prompts to guide users
- Real-time character count
- AI-powered interest classification

### 3. Itinerary Creation
- Multi-day trip planning (1-7 days)
- Date picker for start date
- Customizable daily hours (start/end times)
- Budget category selection (Budget/Moderate/Luxury)
- Real-time itinerary generation

### 4. Itinerary Display
- Day-by-day tabbed interface
- Timeline visualization for each day
- POI details with arrival/departure times
- Visit duration and travel time calculations
- Total distance and stops summary

### 5. Interactive Map
- MapLibre GL JS integration
- Custom POI markers colored by cluster
- Popup information for each location
- Automatic bounds fitting

### 6. Feedback Survey (P1-P16)
- Likert scale questions (P1-P14)
- Text response questions (P15-P16)
- User satisfaction measurement
- Research evaluation framework

## Tech Stack

- **Framework:** React 18 + Vite
- **UI Library:** Material-UI (MUI) v5
- **State Management:** Zustand
- **Routing:** React Router v6
- **Maps:** MapLibre GL JS + react-map-gl
- **HTTP Client:** Axios
- **Date Handling:** date-fns
- **Styling:** MUI theme + Emotion

## Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/
│   ├── Auth/
│   │   ├── Login.jsx              # Login form
│   │   └── Register.jsx           # Registration form
│   ├── Interests/
│   │   └── InterestInput.jsx      # NLC text input
│   ├── Itinerary/
│   │   ├── ItineraryForm.jsx      # Trip configuration
│   │   ├── ItineraryView.jsx      # Optimized itinerary display
│   │   └── DaySchedule.jsx        # Daily timeline
│   ├── Map/
│   │   └── InteractiveMap.jsx     # MapLibre map component
│   ├── Feedback/
│   │   └── SurveyForm.jsx         # P1-P16 survey
│   └── Common/
│       └── Navigation.jsx         # Top navigation bar
├── pages/
│   └── Home.jsx                   # Landing page
├── services/
│   ├── api.js                     # Axios instance + interceptors
│   └── auth.js                    # Authentication service
├── stores/
│   ├── authStore.js               # Auth state management
│   └── itineraryStore.js          # Itinerary state management
├── App.jsx                        # Main app component + routing
└── main.jsx                       # React entry point
```

## Environment Variables

Create a `.env` file in the frontend root:

```
VITE_API_URL=http://localhost:8000
```

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000`.

### Key Endpoints:

**Authentication:**
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/refresh` - Refresh access token

**Interests (Module I):**
- `POST /api/interests/classify` - Classify user text into interest categories
- `GET /api/interests/categories` - Get all interest categories

**Itinerary:**
- `POST /api/itinerary/create` - Create personalized itinerary
- `GET /api/itinerary/{id}` - Get itinerary details
- `GET /api/itinerary/user/{user_id}` - List user's itineraries
- `POST /api/itinerary/{id}/feedback` - Submit survey feedback

## User Flow

1. **Landing Page** → User sees features and benefits
2. **Sign Up/Login** → User creates account or logs in
3. **Interest Input** → User describes preferences in natural language
4. **AI Analysis** → System classifies interests (Module I - NLC)
5. **Trip Configuration** → User selects dates, days, budget
6. **Route Optimization** → System creates itinerary (Modules II-IV)
   - Module II: POI selection with Google popularity scores
   - Module III: K-Means clustering for daily groups
   - Module IV: Genetic algorithm for optimal routes
7. **Itinerary Display** → User views optimized daily schedules
8. **Feedback Survey** → User submits P1-P16 evaluation

## Theme Customization

The app uses a Goa beach-inspired color scheme:
- **Primary:** Ocean Blue (#0277BD)
- **Secondary:** Sunset Orange (#FF6F00)
- **Background:** Light Gray (#F5F5F5)

To customize, edit the `theme` in `App.jsx`.

## State Management

### AuthStore (Zustand)
- `user` - Current user object
- `isAuthenticated` - Boolean auth status
- `login(credentials)` - Login action
- `register(userData)` - Registration action
- `logout()` - Logout action

### ItineraryStore (Zustand)
- `currentItinerary` - Active itinerary object
- `interests` - Classified user interests
- `classifyInterests(text)` - NLC classification
- `createItinerary(data)` - Create new itinerary
- `getItinerary(id)` - Fetch itinerary by ID
- `submitFeedback(id, data)` - Submit survey responses

## Development

### Running Locally

1. Ensure backend is running at `http://localhost:8000`
2. Start frontend dev server: `npm run dev`
3. Open `http://localhost:5173` in browser

### Building for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

### Linting

```bash
npm run lint
```

## Future Enhancements

- [ ] Real-time map updates during route optimization
- [ ] Export itinerary to PDF
- [ ] Share itinerary via link
- [ ] Offline mode with service workers
- [ ] Mobile responsive improvements
- [ ] Dark mode toggle
- [ ] Multi-language support
- [ ] Integration with Google Maps directions API
- [ ] Photos carousel for each POI
- [ ] Weather forecast integration

## Troubleshooting

### CORS Issues
If you encounter CORS errors, ensure the backend's `CORS_ORIGINS` in `.env` includes `http://localhost:5173`.

### Token Expiration
Access tokens expire after 30 minutes. The app automatically refreshes them using the refresh token.

### Map Not Loading
Ensure `maplibre-gl` CSS is imported in the component using the map.

## Contributing

This is an academic final year project. For questions or suggestions, please contact the project team.

## License

Academic project - All rights reserved.
