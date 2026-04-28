---
name: expo-mobile
description: "Use when: ANY Expo/React Native task for WanderWise mobile — UI, navigation, Expo Router, safe area/layout, data fetching, EAS build/config, native modules/config plugins, dev client, SDK upgrades, performance, debugging Metro/Expo Go, and OTA updates."
user-invocable: true
argument-hint: "Describe the Expo/RN task (UI, navigation, data fetching, build, debug, upgrade, performance)."
---

# Expo Mobile Skill (WanderWise)

> Source of truth: https://docs.expo.dev/

## Purpose
Single project-focused skill for all Expo/React Native work in WanderWise. Covers UI, navigation, safe area, data fetching, EAS builds, native modules, dev client, SDK upgrades, CI/CD, performance, and debugging.

---

## When to Use
- Expo/React Native errors (Metro, bundler, runtime, native module issues)
- Safe-area handling or fixed nav layout fixes
- Navigation or screen-flow changes (Expo Router stacks, tabs, modals, sheets)
- Data fetching, API integration, caching, or offline support
- EAS build, config, or app.json/app.config updates
- OTA update configuration or release process
- Dev client builds for testing native code on physical devices
- SDK version upgrades
- Performance tuning for lists, images, or heavy UI screens

---

## General Rules
- Use kebab-case for all file names (e.g. `comment-card.tsx`)
- Always use `import` statements at the top of files
- Never co-locate components, types, or utilities in the `app/` directory — routes only
- Prefer Expo-managed workflow; avoid direct native code edits unless explicitly requested
- Try Expo Go first — only use dev client when custom native code is required
- Prefer aliases over relative imports; configure path aliases in `tsconfig.json`
- Never use removed RN modules: `Picker`, `WebView`, `SafeAreaView` (RN core), `AsyncStorage`
- Always account for safe area (top and bottom insets)

---

## Navigation (Expo Router)
- Use `Stack`, `Tabs`, modals, and form sheets from Expo Router
- Ensure consistent screen registration and deep-link behavior
- Avoid web-only navigation patterns in native screens
- Keep route names stable to avoid breaking existing deep links
- Always remove old route files when restructuring navigation
- Ensure the app always has a route matching `/` (may be inside a group route)
- Use `headerSearchBarOptions` in `Stack.Screen` options to add a search bar

---

## Safe Area + Layout
- **Prefer** `<ScrollView contentInsetAdjustmentBehavior="automatic" />` over `<SafeAreaView>` — it gives smarter insets
- Apply `contentInsetAdjustmentBehavior="automatic"` to `FlatList` and `SectionList` too
- When a route belongs to a Stack, its first child should almost always be a `ScrollView` with `contentInsetAdjustmentBehavior="automatic"`
- Keep one `SafeAreaProvider` at the app root; never nest multiple providers
- Account for bottom insets when using fixed nav bars

---

## UI Patterns
- Follow Apple Human Interface Guidelines for native feel
- Use native controls with built-in haptics: `<Switch />`, `@react-native-community/datetimepicker`
- Use `<Text selectable />` on copyable data
- Format large numbers as `1.4M` or `38k`
- Never use intrinsic HTML elements (`img`, `div`) unless inside a webview or Expo DOM component
- Use Reanimated for animations (runs on UI thread, no JS bridge bottleneck)
- Use `entering`/`exiting`/layout animations from `react-native-reanimated`

---

## Data Fetching
- **Prefer native `fetch` API** — avoid axios unless you specifically need its features; keeps bundle smaller
- Use `expo/fetch` when available
- Never use `axios` by default — use `fetch` with typed error handling

### Fetch patterns
```ts
// Basic GET with error handling
const fetchUser = async (userId: string) => {
  const response = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/users/${userId}`);
  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
  return response.json();
};

// Cancellable fetch
useEffect(() => {
  const controller = new AbortController();
  fetch(url, { signal: controller.signal })
    .then(r => r.json()).then(setData)
    .catch(e => { if (e.name !== 'AbortError') setError(e); });
  return () => controller.abort();
}, [url]);
```

### Caching strategy
- Complex caching / state management → **React Query (TanStack Query)**
- Simpler needs → **SWR** or custom hooks

### Auth tokens
- Store tokens in `expo-secure-store`, never in `AsyncStorage` or `EXPO_PUBLIC_` env vars
- Implement a single refresh flow with `isRefreshing` + `refreshPromise` to prevent parallel refreshes
- Wire `NetInfo` into React Query's `onlineManager` for offline-first support:
```ts
import { onlineManager } from '@tanstack/react-query';
import NetInfo from '@react-native-community/netinfo';
onlineManager.setEventListener(setOnline => 
  NetInfo.addEventListener(state => setOnline(state.isConnected ?? true))
);
```

### Environment variables
- Client-safe keys: `EXPO_PUBLIC_` prefix in `.env` files
- Secret keys: non-prefixed env vars for server/API routes only — never expose in client code
- Use `.env.development` and `.env.production` for per-environment API URLs

---

## EAS Build + App Config
- Prefer `app.json` / `app.config.js` for permissions, icons, splash, and build settings
- Use platform-specific config blocks when needed
- Keep env vars consistent with Expo docs
- `eas.json` example for dev client:
```json
{
  "build": {
    "development": { "developmentClient": true, "autoIncrement": true },
    "production": { "autoIncrement": true }
  }
}
```

---

## Dev Client
- Only create a dev client when the app requires **custom native code** — Expo Go handles most cases
- Build commands:
```bash
# Build dev client via EAS
eas build -p ios --profile development
eas build -p android --profile development

# Local build
eas build -p ios --profile development --local

# Start Metro for dev client
npx expo start --dev-client
```
- Signing errors: `eas credentials`
- Clear build cache: `eas build -p ios --profile development --clear-cache`
- List recent builds: `eas build:list`

---

## Native Modules + Config Plugins
- Use Expo config plugins when a native module requires config changes
- Avoid direct native code edits unless explicitly asked
- A native rebuild (`npx expo run:ios` / `npx expo run:android`) is required after adding native modules

### SwiftUI (expo-ui)
- Import components from `@expo/ui/swift-ui`, modifiers from `@expo/ui/swift-ui/modifiers`
- Every SwiftUI tree must be wrapped in `<Host>`; use `<RNHostView>` to embed RN components inside SwiftUI
- Always check docs before using a component: `https://docs.expo.dev/versions/latest/sdk/ui/swift-ui/{component-name}/index.md`

---

## SDK Upgrades
- Run `npx expo install expo@latest` then follow the upgrade guide
- Check if latest is a beta first: `https://exp.host/--/api/v2/versions`
- Beta versions use `.preview` suffix (e.g. `55.0.0-preview.2`), published under `@next` tag
- **New architecture is enabled by default** from SDK 53+; `"newArchEnabled": true` in `app.json` is no longer needed
- `EXPO_USE_FAST_RESOLVER=1` removed in SDK 54
- Expo webpack is deprecated — migrate to Expo Router + Metro web
- Hermes v1 opt-in (SDK 55): set `useHermesV1: true` in `expo-build-properties`
- If `ios/` and `android/` directories do not exist → project uses CNG; skip bare-workflow cache steps
- For expo-av migrations: audio → `expo-audio`, video → `expo-video`
- Review and remove outdated patches in `patches/` directory after upgrading
- Check `metro.config.js` — if it only contains Expo defaults, delete the file
- `autoprefixer` not needed in SDK 53+

---

## Performance
- Use `FlatList` / `SectionList` for large lists; set `getItemLayout` and `keyExtractor`
- Memoize heavy render paths; avoid inline functions in list rows
- Optimize images with proper sizes and caching strategies
- Use Reanimated for 60fps animations (UI thread, no JS bridge)
- Use `React.memo` to prevent unnecessary re-renders
- Hermes engine is default in Expo SDK 50+

---

## OTA Updates
- Follow Expo Updates conventions and ensure runtime version alignment
- Avoid breaking changes without bumping the runtime version
- Use EAS Update for publishing OTA updates

---

## Debugging
- Clear Metro cache: `npx expo start -c`
- Verify device and dev server IP/port alignment
- Android emulator host: `http://10.0.2.2:<port>`
- Physical device host: `http://<LAN-IP>:<port>`
- Validate `EXPO_PUBLIC_` env vars are set correctly
- Check `eas build:list` / `eas build:view` for build-related issues
- Signing errors: `eas credentials`

---

## Verify Steps
```bash
npx expo start          # Start dev server
npx expo start -c       # Clear cache + start
npx expo run:ios        # Local iOS build
npx expo run:android    # Local Android build
eas build:list          # List recent EAS builds
```

---

## Output Expectations
- Concise change summary with file references
- Only the required commands
- Call out platform-specific gotchas (iOS vs Android)
- Flag if a native rebuild is required after a change