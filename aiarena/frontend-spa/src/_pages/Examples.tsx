import { getFeatureFlags } from "@/_data/featureFlags";

export default function Examples() {
  return (
    <div>
      <h1>Examples</h1>
      <div className="p-10 space-y-4">
        <p className="text-xl font-quicksand">This is Quicksand</p>
        <p className="text-xl font-gugi">This is Gugi</p>
        <p className="text-xl">This is default sans-serif</p>
        {getFeatureFlags().examples && "hi"}
      </div>
    </div>
  );
}
