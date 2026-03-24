import { FileText, Pill, Database } from "lucide-react";

interface CompressionEfficiencyProps {
  originalMB?: string;
  compressedKB?: string;
  reduction?: number;
}

const CompressionEfficiency = ({
  originalMB = "25",
  compressedKB = "50",
  reduction = 99.8,
}: CompressionEfficiencyProps) => {
  return (
    <div className="rounded-xl border p-6">
      <div className="flex items-center gap-2 text-xl font-bold">
        <Database className="h-5 w-5 text-chart-purple" />
        Compression Efficiency
      </div>
      <p className="mt-1 text-sm text-muted-foreground">
        Storage optimization via Triplet-Capsule mapping
      </p>
      <div className="mt-6 flex flex-col items-center gap-3">
        <div className="flex w-full items-center justify-between rounded-lg border p-4">
          <div>
            <p className="text-xs text-muted-foreground">Original Data Size</p>
            <p className="text-2xl font-bold">{originalMB}</p>
          </div>
          <FileText className="h-8 w-8 text-muted-foreground/30" />
        </div>

        <span className="text-muted-foreground">▼</span>

        <div className="flex w-full items-center justify-between rounded-lg border-2 border-chart-purple/30 bg-chart-purple/5 p-4">
          <div>
            <p className="text-xs text-chart-purple">Compressed Capsule Size</p>
            <p className="text-2xl font-bold">{compressedKB}</p>
          </div>
          <Pill className="h-8 w-8 text-chart-pink/40" />
        </div>

        <div className="flex w-full items-center justify-between rounded-lg bg-verified/10 px-4 py-2">
          <span className="text-sm font-medium">Storage Saved:</span>
          <span className="text-lg font-extrabold text-verified">{reduction}%</span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
          <div className="h-full rounded-full bg-verified" style={{ width: `${Math.min(reduction, 100)}%` }} />
        </div>
      </div>
    </div>
  );
};

export default CompressionEfficiency;
