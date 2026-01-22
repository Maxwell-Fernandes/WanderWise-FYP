import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { LogIn, Mail, Lock } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import useAuthStore from '../../stores/authStore';

const Login = () => {
  const [formData, setFormData] = useState({
    email: 'demo@wanderwise.com',
    password: 'password123',
  });

  const navigate = useNavigate();
  const { login } = useAuthStore();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Mock login - bypass authentication for UI testing
    const mockUser = {
      id: '1',
      email: formData.email,
      full_name: 'Demo User',
      username: 'demo_user',
    };

    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 500));

    // Mock login (update store directly)
    useAuthStore.setState({
      user: mockUser,
      isAuthenticated: true,
      isLoading: false,
    });

    // Store in localStorage for persistence
    localStorage.setItem('user', JSON.stringify(mockUser));
    localStorage.setItem('access_token', 'mock-token-12345');

    navigate('/interests');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-orange-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md border-2 shadow-2xl">
        <CardHeader className="space-y-2 text-center">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center">
              <LogIn className="w-8 h-8 text-white" />
            </div>
          </div>
          <CardTitle className="text-3xl font-bold">Welcome Back</CardTitle>
          <CardDescription className="text-base">
            Sign in to plan your perfect Goa adventure
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium">
                Email Address
              </Label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={handleChange}
                  className="pl-10"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium">
                Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                  className="pl-10"
                  required
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input type="checkbox" className="rounded border-gray-300" />
                <span className="text-sm text-gray-600">Remember me</span>
              </label>
              <a href="#" className="text-sm text-primary hover:underline">
                Forgot password?
              </a>
            </div>

            <Button type="submit" className="w-full h-11 text-base font-semibold">
              Sign In
            </Button>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Demo Credentials</span>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-1">
              <p className="text-sm text-gray-700">
                <strong>Email:</strong> demo@wanderwise.com
              </p>
              <p className="text-sm text-gray-700">
                <strong>Password:</strong> password123
              </p>
              <p className="text-xs text-gray-600 mt-2">
                (Any credentials work - this is for UI testing only)
              </p>
            </div>

            <div className="text-center text-sm text-gray-600">
              Don't have an account?{' '}
              <Link to="/register" className="text-primary hover:underline font-medium">
                Sign up here
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default Login;
