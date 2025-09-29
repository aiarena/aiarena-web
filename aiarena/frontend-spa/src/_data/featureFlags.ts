const defaultFlags = {
    examples: false,
    reactRework: false,
};

type FeatureFlags = Record<keyof typeof defaultFlags, boolean>;

// Set this to true to override default (show all) DEV behavior - simulate how the site looks in production
const simulateProductionEnv = false;

export function getFeatureFlags(): FeatureFlags {
    // Feature Flags - false =  hide, true = show

    // console.log(process.env.NODE_ENV)
    // console.log(import.meta.env.DEV)
    const hideSelectFeatures =
        import.meta.env.DEV && !simulateProductionEnv;

    // If DEV mode is enabled, set all flags to true
    if (hideSelectFeatures) {
        return Object.fromEntries(
            Object.keys(defaultFlags).map((key) => [key, true]),
        ) as FeatureFlags;
    }

    return defaultFlags;
}
