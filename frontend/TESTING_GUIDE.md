# WanderWise+ Frontend Testing Guide

## Server Status
**Running on:** http://localhost:5173/

## Complete User Flow - Test This Now!

### Step 1: Home Page
- Open: http://localhost:5173/
- You should see: Beautiful landing page with gradient hero, features, and stats
- Test: Click "Get Started" or "Sign In" buttons

### Step 2: Register (if clicked Get Started)
- URL: http://localhost:5173/register
- Form fields: Full Name, Email, Password, Confirm Password
- Test: Fill form and click "Create Account"
- Result: Auto-login and redirect to /interests

### Step 3: Login (if clicked Sign In)
- URL: http://localhost:5173/login  
- Pre-filled: demo@wanderwise.com / password123
- Test: Click "Sign In" (or use any credentials)
- Result: Redirect to /interests

### Step 4: Interest Input
- URL: http://localhost:5173/interests
- You should see: Text area for preferences, example prompts
- Test:
  1. Click any example prompt (auto-fills text)
  2. Click "Analyze with AI"
  3. Wait 2 seconds for loading animation
  4. See colored progress bars showing interest analysis
  5. Click "Continue to Trip Planning"
- Result: Redirect to /create-itinerary

### Step 5: Itinerary Form
- URL: http://localhost:5173/create-itinerary
- Form fields:
  - Number of days (1-7)
  - Start date (date picker)
  - Start time / End time
  - Budget (Budget/Moderate/Luxury buttons)
- Test: Fill form and click "Generate Itinerary"
- Result: 3-second loading, then redirect to /itinerary/itin-123

### Step 6: Itinerary View
- URL: http://localhost:5173/itinerary/itin-123
- **CURRENTLY USING MUI** - Functional but not Tailwind styled
- You should see:
  - Summary stats (3 days, 145.6 km, 6 stops)
  - Day tabs (Day 1, Day 2, Day 3)
  - Timeline of places for selected day
  - Each place shows: time, duration, distance
- Test: Click different day tabs

### Step 7: Survey Form
- URL: http://localhost:5173/survey/itin-123
- **CURRENTLY USING MUI** - Functional but not Tailwind styled
- You should see:
  - Likert scale questions (P1-P14)
  - Text response questions (P15-P16)
- Test: Fill and submit survey

## What's Working (Tailwind + shadcn/ui)
✅ Home Page - Complete
✅ Login - Complete  
✅ Register - Complete
✅ Interest Input - Complete
✅ Itinerary Form - Complete

## What's Functional (MUI - Works but different style)
⚠️ Itinerary View - Shows data, functional
⚠️ Survey Form - Shows data, functional

## Known Issues to Fix
1. Navigation bar needs to update after login
2. Itinerary View needs Tailwind redesign
3. Survey Form needs Tailwind redesign

## Quick Test Commands

# Test login flow
1. Go to http://localhost:5173/
2. Click "Sign In"
3. Click "Sign In" button (demo credentials work)
4. Should redirect to /interests

# Test full registration flow  
1. Go to http://localhost:5173/
2. Click "Get Started"
3. Fill form (any data works)
4. Should auto-login and redirect to /interests

# Test interest analysis
1. Go to /interests (must be logged in)
2. Click first example prompt
3. Click "Analyze with AI"
4. Wait 2 seconds
5. Should show progress bars
6. Click "Continue"

# Test itinerary generation
1. Go to /create-itinerary (must complete interests)
2. Fill form with any data
3. Click "Generate Itinerary"
4. Wait 3 seconds
5. Should redirect to /itinerary/itin-123

## Mock Data Being Used
- User: demo@wanderwise.com
- Itinerary ID: itin-123
- 6 sample places (Baga Beach, Basilica, Dudhsagar, Fort Aguada, Palolem, Spice Plantation)
- 3-day schedule with full timeline

## Browser Console
Open DevTools (F12) → Console tab to see:
- Navigation events
- Store state updates
- Any errors

## Next Steps Needed
1. Update Navigation to show logged-in user
2. Create Tailwind version of Itinerary View
3. Create Tailwind version of Survey Form
4. Add loading states
5. Add error handling
