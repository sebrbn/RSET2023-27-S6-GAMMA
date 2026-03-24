import { Shield, Target, HardDrive, TrendingUp } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer } from "recharts";

interface PerformanceMetricsProps {
  truthScore: number;
  accuracy: number;
  compression: {
    fileName: string;
    originalSize: string;
    compressedSize: string;
    reduction: string;
  };
  trendData: { query: number; score: number }[];
  onAuditLabClick: () => void;
}

const PerformanceMetrics = ({
  truthScore,
  accuracy,
  compression,
  trendData,
  onAuditLabClick,
}: PerformanceMetricsProps) => {
  return (
    <div className="flex h-full w-80 shrink-0 flex-col gap-4 overflow-y-auto border-l p-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">Performance Metrics</h2>
        <button
          onClick={onAuditLabClick}
          className="flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-secondary"
        >
          <Shield className="h-3.5 w-3.5" />
          Audit Lab
        </button>
      </div>

      {/* Truth Score */}
      <div className="metric-card border-verified/30 bg-verified/5">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <Shield className="h-4 w-4 text-verified" />
          Truth Score
        </div>
        <p className="mt-2 text-4xl font-extrabold text-verified">{truthScore}</p>
        <p className="mt-1 text-xs text-muted-foreground">Current reliability rating</p>
        <p className="mt-3 text-xs text-muted-foreground italic">
          Note: <span className="text-foreground">If accuracy starts to fall and reaches 70% or lower, upload the current document again.</span>
        </p>
      </div>

      {/* Accuracy */}
      <div className="metric-card border-chart-purple/30 bg-chart-purple/5">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <Target className="h-4 w-4 text-chart-purple" />
          Accuracy
        </div>
        <p className="mt-2 text-4xl font-extrabold text-verified">{accuracy}%</p>
        <p className="mt-1 text-xs text-muted-foreground">Response accuracy rate</p>
      </div>

      {/* Memory Compression */}
      <div className="metric-card">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <HardDrive className="h-4 w-4 text-primary" />
          Memory Compression
        </div>
        <div className="mt-3 space-y-2 text-sm">
          <p className="text-muted-foreground">
            File: <span className="font-medium text-foreground">{compression.fileName}</span>
          </p>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Original:</span>
            <span className="font-semibold">{compression.originalSize}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Compressed:</span>
            <span className="font-semibold text-verified">{compression.compressedSize}</span>
          </div>
          <p className="text-center text-xs text-primary">{compression.reduction} size reduction</p>
        </div>
      </div>

      {/* Truth Score Trend */}
      <div className="metric-card">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <TrendingUp className="h-4 w-4 text-chart-pink" />
          Truth Score Trend
        </div>
        <div className="mt-3 h-36">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={trendData}>
              <XAxis dataKey="query" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} domain={[0, 100]} />
              <Bar dataKey="score" fill="hsl(330, 81%, 60%)" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <p className="mt-1 text-center text-xs text-muted-foreground">Last 10 responses</p>
      </div>

      {/* Score Guide */}
      <div className="metric-card">
        <h3 className="text-sm font-semibold">Score Guide</h3>
        <div className="mt-2 space-y-1.5 text-xs">
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-verified" />
            80-100: Excellent
          </div>
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-warning" />
            60-79: Good
          </div>
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-contradiction" />
            0-59: Needs Review
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceMetrics;
