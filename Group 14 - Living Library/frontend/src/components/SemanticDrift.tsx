import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { TrendingDown } from "lucide-react";

const driftData = [
  { q: "Q1", drift: 2.1 },
  { q: "Q2", drift: 1.8 },
  { q: "Q3", drift: 3.1 },
  { q: "Q4", drift: 2.4 },
  { q: "Q5", drift: 1.9 },
  { q: "Q6", drift: 1.6 },
  { q: "Q7", drift: 2.8 },
  { q: "Q8", drift: 2.5 },
  { q: "Q9", drift: 1.8 },
  { q: "Q10", drift: 2.2 },
];

const SemanticDrift = () => {
  return (
    <div className="rounded-xl border p-6">
      <div className="flex items-center gap-2 text-xl font-bold">
        <TrendingDown className="h-5 w-5 text-chart-orange" />
        Semantic Drift Analysis
      </div>
      <p className="mt-1 text-sm text-muted-foreground">
        Deviation from original PDF facts over time
      </p>
      <div className="mt-4 h-52">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={driftData}>
            <XAxis dataKey="q" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} domain={[0, 4]} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="drift"
              stroke="hsl(25, 95%, 53%)"
              strokeWidth={2.5}
              dot={{ fill: "hsl(25, 95%, 53%)", r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="info-banner mt-4">
        <strong>Average Drift:</strong> 2.35% | Lower is better. Indicates how much the AI's
        understanding diverges from source material.
      </div>
    </div>
  );
};

export default SemanticDrift;
