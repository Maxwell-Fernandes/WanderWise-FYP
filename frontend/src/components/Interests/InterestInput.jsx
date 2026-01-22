import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Lightbulb, ArrowRight, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Label } from '../ui/label';
import { mockInterests } from '../../data/mockData';
import useItineraryStore from '../../stores/itineraryStore';

const InterestInput = () => {
  const [userInput, setUserInput] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzedInterests, setAnalyzedInterests] = useState(null);
  const navigate = useNavigate();

  const examplePrompts = [
    "I love beaches, water sports, and trying local seafood. Looking for adventure and relaxation.",
    "Interested in Portuguese colonial history, old churches, and forts. I'm a culture enthusiast.",
    "Want to explore waterfalls, spice plantations, and nature trails. Photography is my passion.",
    "Nightlife, beach parties, live music, and happening clubs. Party vibes!",
  ];

  const handleAnalyze = async () => {
    if (!userInput.trim()) return;

    setIsAnalyzing(true);

    // Simulate AI analysis delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Mock interest classification
    const interests = { ...mockInterests };
    setAnalyzedInterests(interests);

    // Store in zustand
    useItineraryStore.setState({ interests });

    setIsAnalyzing(false);
  };

  const handleContinue = () => {
    navigate('/create-itinerary');
  };

  const getInterestColor = (score) => {
    if (score >= 0.8) return 'bg-green-500';
    if (score >= 0.6) return 'bg-blue-500';
    if (score >= 0.4) return 'bg-yellow-500';
    return 'bg-gray-400';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-orange-50 py-8">
      <div className="container mx-auto px-4 max-w-5xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-[--color-primary] to-[--color-secondary] rounded-full flex items-center justify-center">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Tell Us Your Interests</h1>
          <p className="text-lg text-gray-600">
            Describe what you'd like to experience in Goa, and our AI will understand your preferences
          </p>
        </div>

        {/* Main Card */}
        <Card className="border-2 shadow-xl mb-6">
          <CardHeader>
            <CardTitle className="text-2xl">Share Your Travel Preferences</CardTitle>
            <CardDescription className="text-base">
              Write in natural language - just like talking to a friend!
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Text Area */}
            <div className="space-y-2">
              <Label htmlFor="interests" className="text-base font-semibold">
                What are you looking for in your Goa trip?
              </Label>
              <textarea
                id="interests"
                rows={6}
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="E.g., I'm looking for a mix of adventure and relaxation. Love water sports, scenic beaches, and trying authentic Goan cuisine. Also interested in historical sites and photography spots..."
                className="w-full rounded-md border border-gray-300 bg-white px-4 py-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[--color-primary] focus-visible:ring-offset-2 resize-none"
              />
              <p className="text-sm text-gray-500 text-right">
                {userInput.length} / 500 characters
              </p>
            </div>

            {/* Action Button */}
            <Button
              onClick={handleAnalyze}
              disabled={!userInput.trim() || isAnalyzing}
              size="lg"
              className="w-full text-base font-semibold"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Analyzing Your Interests...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5 mr-2" />
                  Analyze with AI
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Example Prompts */}
        <Card className="border-2 mb-6">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <Lightbulb className="w-5 h-5 text-yellow-500" />
              <CardTitle className="text-xl">Need Inspiration?</CardTitle>
            </div>
            <CardDescription>Click any example to try it out</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {examplePrompts.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => setUserInput(prompt)}
                  className="text-left p-4 rounded-lg border border-gray-200 hover:border-[--color-primary] hover:bg-blue-50 transition-colors text-sm"
                >
                  "{prompt}"
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Analysis Results */}
        {analyzedInterests && (
          <Card className="border-2 shadow-xl">
            <CardHeader>
              <CardTitle className="text-2xl flex items-center">
                <Sparkles className="w-6 h-6 mr-2 text-green-500" />
                Interest Analysis Complete!
              </CardTitle>
              <CardDescription className="text-base">
                Here's what our AI understood about your preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Interest Bars */}
              <div className="space-y-4">
                {Object.entries(analyzedInterests).map(([interest, score]) => (
                  <div key={interest} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium capitalize">{interest}</span>
                      <span className="text-sm font-semibold text-gray-700">
                        {Math.round(score * 100)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                      <div
                        className={`h-full ${getInterestColor(score)} transition-all duration-500`}
                        style={{ width: `${score * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Continue Button */}
              <Button
                onClick={handleContinue}
                size="lg"
                className="w-full text-base font-semibold"
              >
                Continue to Trip Planning
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Info Section */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-600">
            <strong>Module I - NLC:</strong> Natural Language Classification powered by AI
          </p>
          <p className="text-xs text-gray-500 mt-2">
            Your preferences are analyzed to create personalized recommendations
          </p>
        </div>
      </div>
    </div>
  );
};

export default InterestInput;
