import { WorkbenchDataProvider } from "@/app/(dashboard)/workbench/workbench-data";
import { WorkbenchFrame } from "@/app/(dashboard)/workbench/workbench-frame";

/** Shares dictionary and database state across all workbench destinations. */
export default function WorkbenchLayout({ children }: { children: React.ReactNode }) {
  return (
    <WorkbenchDataProvider>
      <WorkbenchFrame>
        {children}
      </WorkbenchFrame>
    </WorkbenchDataProvider>
  );
}
