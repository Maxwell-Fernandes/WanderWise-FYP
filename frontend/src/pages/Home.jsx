import { useNavigate } from 'react-router-dom';
import { MapPin, Calendar, Route, TrendingUp, Sparkles, Clock } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import useAuthStore from '../stores/authStore';

const Home = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuthStore();

  const features = [
    {
      icon: <Sparkles className="w-12 h-12 text-primary" />,
      title: 'AI-Powered Recommendations',
      description: 'Tell us your interests in natural language and our AI will understand what you love',
    },
    {
      icon: <Route className="w-12 h-12 text-primary" />,
      title: 'Smart Route Optimization',
      description: 'We use advanced algorithms to create the most efficient routes across Goa',
    },
    {
      icon: <Calendar className="w-12 h-12 text-primary" />,
      title: 'Personalized Schedules',
      description: 'Get day-by-day itineraries with optimal timing for each destination',
    },
    {
      icon: <TrendingUp className="w-12 h-12 text-primary" />,
      title: 'Research-Backed',
      description: 'Built on cutting-edge research in route optimization and recommendation systems',
    },
  ];

  const steps = [
    {
      number: '1',
      title: 'Share Interests',
      description: 'Tell us what you love in your own words',
    },
    {
      number: '2',
      title: 'AI Analysis',
      description: 'Our NLP system understands your preferences',
    },
    {
      number: '3',
      title: 'Smart Clustering',
      description: 'POIs grouped geographically for efficient travel',
    },
    {
      number: '4',
      title: 'Optimized Route',
      description: 'Genetic algorithm creates your perfect itinerary',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-50 to-white">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16 md:py-24">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <div className="space-y-4">
            <h1 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              WanderWise+
            </h1>
            <p className="text-2xl md:text-3xl text-gray-700 font-medium">
              Your Intelligent Goa Tourism Route Planner
            </p>
          </div>

          <p className="text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Discover the perfect Goa experience with our AI-powered itinerary planner. Using
            advanced Natural Language Processing, K-Means clustering, and Genetic Algorithms,
            we create personalized multi-day routes just for you.
          </p>

          {isAuthenticated ? (
            <div className="space-y-4">
              <p className="text-xl font-semibold text-gray-800">
                Welcome back, {user?.full_name || user?.username || 'Traveler'}! 👋
              </p>
              <Button
                size="lg"
                onClick={() => navigate('/interests')}
                className="text-lg px-8 py-6 h-auto"
              >
                <MapPin className="w-5 h-5 mr-2" />
                Create New Itinerary
              </Button>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button
                size="lg"
                onClick={() => navigate('/register')}
                className="text-lg px-8 py-6 h-auto"
              >
                Get Started
              </Button>
              <Button
                size="lg"
                variant="outline"
                onClick={() => navigate('/login')}
                className="text-lg px-8 py-6 h-auto"
              >
                Sign In
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Features Grid */}
      <div className="container mx-auto px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow border-2">
              <CardHeader>
                <div className="mb-4">{feature.icon}</div>
                <CardTitle className="text-xl">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">{feature.description}</CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* How It Works */}
      <div className="container mx-auto px-4 py-16">
        <Card className="border-2 shadow-xl">
          <CardHeader className="text-center pb-8">
            <CardTitle className="text-4xl font-bold">How It Works</CardTitle>
            <CardDescription className="text-lg mt-2">
              Your journey to the perfect Goa experience in 4 simple steps
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {steps.map((step, index) => (
                <div key={index} className="text-center space-y-4">
                  <div className="flex justify-center">
                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                      {step.number}
                    </div>
                  </div>
                  <h3 className="text-xl font-semibold">{step.title}</h3>
                  <p className="text-gray-600">{step.description}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Stats Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="text-center border-2">
            <CardHeader>
              <CardTitle className="text-5xl font-bold text-primary">100+</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xl font-medium text-gray-700">Curated Locations</p>
              <p className="text-gray-600 mt-2">Handpicked destinations across Goa</p>
            </CardContent>
          </Card>
          <Card className="text-center border-2">
            <CardHeader>
              <CardTitle className="text-5xl font-bold text-primary">
                <Clock className="w-12 h-12 mx-auto" />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xl font-medium text-gray-700">Save Hours</p>
              <p className="text-gray-600 mt-2">Optimized routes save planning time</p>
            </CardContent>
          </Card>
          <Card className="text-center border-2">
            <CardHeader>
              <CardTitle className="text-5xl font-bold text-primary">AI</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xl font-medium text-gray-700">Powered</p>
              <p className="text-gray-600 mt-2">Natural language understanding</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Home;
