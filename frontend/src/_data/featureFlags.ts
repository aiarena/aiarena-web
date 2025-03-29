// Define the type for feature flags
type FeatureFlags = {
  heroTasks: boolean;
  heroDiscordUsersInfo: boolean;
  footerServices: boolean;
  statusServerStatus: boolean;
  statusPage: boolean;
  botsPage: boolean;
  competitionMaps: boolean;
  competitionVideo: boolean;
  supporters: boolean;
  examples: boolean;
};

// Set this to true to override DEV behavior
const devBehaviorOverride = true;

// Feature flags configuration function
export function getFeatureFlags(): FeatureFlags {
  // Check if DEV mode is enabled and not overridden
  const isDevMode =
    process.env.NODE_ENV === "development" && !devBehaviorOverride;

  // Default feature flags
  const defaultFlags: FeatureFlags = {
    heroTasks: false,
    heroDiscordUsersInfo: false,
    footerServices: false,
    statusServerStatus: false,
    statusPage: true,
    botsPage: true,
    competitionMaps: true,
    competitionVideo: false,
    supporters: true,
    examples: false,
  };

  // If DEV mode is enabled, set all flags to true
  if (isDevMode) {
    return Object.fromEntries(
      Object.keys(defaultFlags).map((key) => [key, true]),
    ) as FeatureFlags; // Cast the result to the FeatureFlags type
  }

  // Return default flags in other cases
  return defaultFlags;
}
