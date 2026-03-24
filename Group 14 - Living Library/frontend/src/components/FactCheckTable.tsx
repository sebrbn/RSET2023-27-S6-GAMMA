import { CheckCircle2, XCircle, HelpCircle, ExternalLink, ShieldAlert } from "lucide-react";

export interface Claim {
  id: string;
  claim: string;
  sourceCapsule: string;
  status: "verified" | "contradiction" | "neutral";
}

const statusConfig = {
  verified: {
    label: "Verified",
    icon: CheckCircle2,
    className: "status-verified",
  },
  contradiction: {
    label: "Contradiction",
    icon: XCircle,
    className: "status-contradiction",
  },
  neutral: {
    label: "Neutral/External",
    icon: HelpCircle,
    className: "status-neutral",
  },
};

export const FactCheckTable = ({ claims = [] }: { claims?: Claim[] }) => {
  // Deduplicate claims by their string value to avoid duplicate triplets
  const uniqueClaims = claims.filter((claim, index, self) =>
    index === self.findIndex((c) => c.claim === claim.claim)
  );

  // 1. Guard against empty data to prevent crashes
  if (!uniqueClaims || uniqueClaims.length === 0) {
    return (
      <div className="rounded-xl border p-12 text-center bg-card">
        <ShieldAlert className="mx-auto h-10 w-10 text-muted-foreground/50 mb-4" />
        <h3 className="font-semibold text-lg">No Audit Data Yet</h3>
        <p className="text-sm text-muted-foreground mt-1">
          Upload a file or ask a question to start the truth verification process.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border p-6 bg-card shadow-sm">
      <h2 className="text-xl font-bold">RefChecker: Fact-Check Center</h2>
      <p className="mt-1 text-sm text-muted-foreground">
        Verification of AI claims against extracted knowledge triples
      </p>
      <div className="mt-5 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              <th className="pb-3">AI Claim</th>
              <th className="pb-3">Source Capsule</th>
              <th className="pb-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {uniqueClaims.map((claim, index) => {
              // 2. Defensive config check
              const status = claim.status || "neutral";
              const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.neutral;
              const Icon = config.icon;

              return (
                <tr key={claim.id || index} className="group hover:bg-muted/30 transition-colors">
                  <td className="py-4 pr-4">
                    <code className="rounded bg-secondary px-2 py-1 text-xs font-medium break-words">
                      {claim.claim}
                    </code>
                  </td>
                  <td className="py-4">
                    <div className="flex items-center gap-1 text-primary cursor-default">
                      <span className="truncate max-w-[150px]">{claim.sourceCapsule || "Source Triple"}</span>
                      <ExternalLink className="h-3 w-3" />
                    </div>
                  </td>
                  <td className="py-4">
                    <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${config.className}`}>
                      <Icon className="h-3.5 w-3.5" />
                      {config.label}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default FactCheckTable;