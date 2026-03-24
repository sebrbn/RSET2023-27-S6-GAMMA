import { Activity } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } from "recharts";

const stabilityData = Array.from({ length: 10 }, (_, i) => ({
  query: `Q${i + 1}`,
  score: 75 + Math.floor(Math.random() * 20),
}));

const TruthScoreStability = () => {
  return (
    <div className="rounded-xl border p-6">
      <div className="flex items-center gap-2 text-xl font-bold">
        <Activity className="h-5 w-5 text-primary" />
        Truth Score Stability
      </div>
      <p className="mt-1 text-sm text-muted-foreground">
        System reliability across last 10 queries
      </p>
      <div className="mt-4 h-52">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={stabilityData}>
            <XAxis dataKey="query" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
            <Tooltip />
            <Bar dataKey="score" fill="hsl(221, 83%, 53%)" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default TruthScoreStability;
