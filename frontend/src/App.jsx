import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navigation from './components/Common/Navigation';
import Home from './pages/Home';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import InterestInput from './components/Interests/InterestInput';
import ItineraryForm from './components/Itinerary/ItineraryFormNew';
import ItineraryView from './components/Itinerary/ItineraryView';
import SurveyForm from './components/Feedback/SurveyForm';
import useAuthStore from './stores/authStore';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        <Navigation />
        <main className="flex-grow">
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<ItineraryForm />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Routes */}
            <Route
              path="/interests"
              element={
                <ProtectedRoute>
                  <InterestInput />
                </ProtectedRoute>
              }
            />
            <Route
              path="/create-itinerary"
              element={
                <ProtectedRoute>
                  <ItineraryForm />
                </ProtectedRoute>
              }
            />
            <Route
              path="/itinerary/:itineraryId"
              element={
                <ProtectedRoute>
                  <ItineraryView />
                </ProtectedRoute>
              }
            />
            <Route
              path="/survey/:itineraryId"
              element={
                <ProtectedRoute>
                  <SurveyForm />
                </ProtectedRoute>
              }
            />

            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-gray-100 border-t border-gray-200 py-8">
          <div className="container mx-auto px-4 text-center space-y-2">
            <p className="text-gray-700 font-medium">
              WanderWise+ © {new Date().getFullYear()} - Intelligent Tourism Route Planning
            </p>
            <p className="text-sm text-gray-600">
              Powered by NLP, K-Means Clustering & Genetic Algorithms
            </p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
