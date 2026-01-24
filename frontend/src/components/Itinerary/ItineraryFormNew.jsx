import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, Clock, DollarSign, MapPin, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import useItineraryStore from '../../stores/itineraryStore';

const ItineraryFormNew = () => {
  const [formData, setFormData] = useState({
    numDays: 3,
    startDate: '2024-12-15',
    startTime: '09:00',
    endTime: '18:00',
    budgetCategory: 'Moderate',
  });
  const [isGenerating, setIsGenerating] = useState(true);
  const navigate = useNavigate();
  const { createItinerary } = useItineraryStore();
  
  // Automatically submit form when component loads
  useEffect(() => {
    const submit = async () => {
      const itineraryData = {
        numDays: formData.numDays,
        startDate: formData.startDate,
        startTime: formData.startTime,
        endTime: formData.endTime,
        budgetCategory: formData.budgetCategory,
      };
      
      try {
        const itinerary = await createItinerary(itineraryData);
        navigate(`/itinerary/${itinerary.id || 'itin-123'}`);
      } catch (error) {
        console.error('Error generating itinerary:', error);
        setIsGenerating(false);
      }
    };
    submit();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsGenerating(true);

    try {
      const itineraryData = {
        numDays: formData.numDays,
        startDate: formData.startDate,
        startTime: formData.startTime,
        endTime: formData.endTime,
        budgetCategory: formData.budgetCategory,
      };
      
      const itinerary = await createItinerary(itineraryData);
      
      setIsGenerating(false);
      navigate(`/itinerary/${itinerary.id || 'itin-123'}`);
    } catch (error) {
      console.error('Error generating itinerary:', error);
      setIsGenerating(false);
    }
  };

  const budgetOptions = ['Budget', 'Moderate', 'Luxury'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-orange-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-[--color-primary] to-[--color-secondary] rounded-full flex items-center justify-center">
              <Calendar className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Plan Your Trip</h1>
          <p className="text-lg text-gray-600">
            Configure your travel dates and preferences
          </p>
        </div>

        <Card className="border-2 shadow-xl">
          <CardHeader>
            <CardTitle className="text-2xl">Trip Configuration</CardTitle>
            <CardDescription className="text-base">
              Let us know when you're visiting and we'll create the perfect itinerary
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Submit Button (Visible at top) */}
              <Button
                type="submit"
                disabled={isGenerating}
                size="lg"
                className="w-full text-base font-semibold"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Generating Your Perfect Itinerary...
                  </>
                ) : (
                  'Generate Itinerary'
                )}
              </Button>
              {/* Number of Days */}
              <div className="space-y-2">
                <Label htmlFor="numDays" className="text-base font-semibold flex items-center">
                  <MapPin className="w-4 h-4 mr-2" />
                  How many days are you staying?
                </Label>
                <Input
                  id="numDays"
                  type="number"
                  min="1"
                  max="7"
                  value={formData.numDays}
                  onChange={(e) => setFormData({ ...formData, numDays: parseInt(e.target.value) })}
                  className="text-base"
                />
                <p className="text-sm text-gray-500">Choose between 1-7 days</p>
              </div>

              {/* Start Date */}
              <div className="space-y-2">
                <Label htmlFor="startDate" className="text-base font-semibold flex items-center">
                  <Calendar className="w-4 h-4 mr-2" />
                  When does your trip start?
                </Label>
                <Input
                  id="startDate"
                  type="date"
                  value={formData.startDate}
                  onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
                  className="text-base"
                />
              </div>

              {/* Daily Hours */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="startTime" className="text-base font-semibold flex items-center">
                    <Clock className="w-4 h-4 mr-2" />
                    Daily Start Time
                  </Label>
                  <Input
                    id="startTime"
                    type="time"
                    value={formData.startTime}
                    onChange={(e) => setFormData({ ...formData, startTime: e.target.value })}
                    className="text-base"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="endTime" className="text-base font-semibold flex items-center">
                    <Clock className="w-4 h-4 mr-2" />
                    Daily End Time
                  </Label>
                  <Input
                    id="endTime"
                    type="time"
                    value={formData.endTime}
                    onChange={(e) => setFormData({ ...formData, endTime: e.target.value })}
                    className="text-base"
                  />
                </div>
              </div>

              {/* Budget Category */}
              <div className="space-y-2">
                <Label className="text-base font-semibold flex items-center">
                  <DollarSign className="w-4 h-4 mr-2" />
                  Budget Category
                </Label>
                <div className="grid grid-cols-3 gap-3">
                  {budgetOptions.map((budget) => (
                    <button
                      key={budget}
                      type="button"
                      onClick={() => setFormData({ ...formData, budgetCategory: budget })}
                      className={`p-4 rounded-lg border-2 text-center transition-all ${
                        formData.budgetCategory === budget
                          ? 'border-[--color-primary] bg-blue-50 font-semibold'
                          : 'border-gray-300 hover:border-gray-400'
                      }`}
                    >
                      {budget}
                    </button>
                  ))}
                </div>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={isGenerating}
                size="lg"
                className="w-full text-base font-semibold"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Generating Your Perfect Itinerary...
                  </>
                ) : (
                  'Generate Itinerary'
                )}
              </Button>

              {isGenerating && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-gray-700 text-center">
                    <strong>AI is working its magic...</strong>
                    <br />
                    Module II: Selecting best POIs • Module III: Clustering locations • Module IV: Optimizing routes
                  </p>
                </div>
              )}
            </form>
          </CardContent>
        </Card>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            <strong>Modules II-IV:</strong> POI Selection • K-Means Clustering • Genetic Algorithm Optimization
          </p>
        </div>
      </div>
    </div>
  );
};

export default ItineraryFormNew;
